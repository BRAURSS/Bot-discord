"""
Cog de Tickets - Système de support par tickets
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import database
from config import Config, Colors, Emojis
import logging

logger = logging.getLogger(__name__)

class TicketButton(View):
    """Bouton pour créer un ticket"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Créer un Ticket", style=discord.ButtonStyle.green, emoji=Emojis.TICKET, custom_id="create_ticket")
    async def create_ticket_button(self, interaction: discord.Interaction, button: Button):
        """Créer un ticket quand le bouton est cliqué"""
        await interaction.response.defer(ephemeral=True)
        
        # Vérifier si l'utilisate a déjà un ticket ouvert
        for channel in interaction.guild.text_channels:
            if channel.name == f"ticket-{interaction.user.name.lower()}":
                return await interaction.followup.send(
                    f"{Emojis.ERROR} Vous avez déjà un ticket ouvert : {channel.mention}",
                    ephemeral=True
                )
        
        # Récupérer ou créer la catégorie
        config = await database.get_guild_config(interaction.guild.id)
        category = None
        
        if config['ticket_category_id']:
            category = interaction.guild.get_channel(config['ticket_category_id'])
        
        if not category:
            # Créer la catégorie
            category = await interaction.guild.create_category(Config.TICKET_CATEGORY_NAME)
            await database.update_guild_config(interaction.guild.id, ticket_category_id=category.id)
        
        # Créer le salon du ticket
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await category.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            reason=f"Ticket créé par {interaction.user}"
        )
        
        # Enregistrer dans la base de données
        ticket_number = await database.create_ticket(interaction.guild.id, channel.id, interaction.user.id)
        
        # Message d'accueil
        embed = discord.Embed(
            title=f"{Emojis.TICKET} Ticket #{ticket_number}",
            description=f"Bienvenue {interaction.user.mention} !\n\nUn membre du staff vous répondra bientôt.\nExpliquez votre problème ou votre question.",
            color=Colors.INFO
        )
        embed.set_footer(text="Utilisez /close pour fermer le ticket | /delete pour le supprimer")
        
        # Bouton de fermeture
        close_view = View(timeout=None)
        close_button = Button(label="Fermer le Ticket", style=discord.ButtonStyle.red, emoji=Emojis.LOCK, custom_id=f"close_ticket_{channel.id}")
        
        async def close_callback(inter: discord.Interaction):
            if inter.user.guild_permissions.manage_channels or inter.user == interaction.user:
                await self._close_ticket(inter, channel)
            else:
                await inter.response.send_message(
                    f"{Emojis.ERROR} Seul le créateur du ticket ou un modérateur peut le fermer.",
                    ephemeral=True
                )
        
        close_button.callback = close_callback
        close_view.add_item(close_button)
        
        await channel.send(embed=embed, view=close_view)
        
        await interaction.followup.send(
            f"{Emojis.SUCCESS} Votre ticket a été créé : {channel.mention}",
            ephemeral=True
        )
        
        logger.info(f"Ticket #{ticket_number} créé par {interaction.user}")
    
    async def _close_ticket(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Ferme un ticket (étape 1 - retire l'accès aux non-mods)"""
        await interaction.response.defer()
        
        # Récupérer les infos du ticket
        ticket = await database.get_ticket(channel.id)
        if not ticket:
            return
        
        # Marquer comme fermé dans la DB
        await database.close_ticket(channel.id)
        
        # Retirer l'accès au créateur du ticket
        creator = interaction.guild.get_member(ticket['user_id'])
        if creator:
            await channel.set_permissions(
                creator,
                read_messages=False,
                send_messages=False
            )
        
        # Renommer le canal pour indiquer qu'il est fermé
        new_name = f"closed-{channel.name}" if not channel.name.startswith("closed-") else channel.name
        await channel.edit(name=new_name)
        
        # Message de fermeture avec bouton de suppression
        embed = discord.Embed(
            title=f"{Emojis.LOCK} Ticket fermé",
            description=f"Ce ticket a été fermé par {interaction.user.mention}\\n\\n"
                       f"Le ticket reste accessible aux modérateurs.\\n"
                       f"Utilisez le bouton ci-dessous pour le supprimer définitivement.",
            color=Colors.WARNING
        )
        
        # Créer le bouton de suppression
        delete_view = View(timeout=None)
        delete_button = Button(
            label="Supprimer le Ticket", 
            style=discord.ButtonStyle.danger, 
            emoji="🗑️",
            custom_id=f"delete_ticket_{channel.id}"
        )
        
        async def delete_callback(inter: discord.Interaction):
            # Vérifier permissions
            if not inter.user.guild_permissions.manage_channels:
                return await inter.response.send_message(
                    f"{Emojis.ERROR} Seuls les modérateurs peuvent supprimer un ticket.",
                    ephemeral=True
                )
            
            # Confirmation de suppression
            await inter.response.send_message(
                f"{Emojis.LOADING} Suppression du ticket...",
                ephemeral=True
            )
            await channel.delete(reason=f"Ticket supprimé par {inter.user}")
        
        delete_button.callback = delete_callback
        delete_view.add_item(delete_button)
        
        await channel.send(embed=embed, view=delete_view)
        
        logger.info(f"Ticket {channel.name} fermé par {interaction.user}")

class Tickets(commands.Cog):
    """Système de tickets pour le support"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # ===== SETUP =====
    @app_commands.command(name="ticketsetup", description="Configurer le système de tickets")
    @app_commands.describe(channel="Le salon où envoyer le message de ticket")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_setup(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """Configure le système de tickets"""
        channel = channel or interaction.channel
        
        embed = discord.Embed(
            title=f"{Emojis.TICKET} Système de Support",
            description="Besoin d'aide ? Cliquez sur le bouton ci-dessous pour créer un ticket !\n\n"
                       "Notre équipe vous répondra dès que possible.",
            color=Colors.INFO
        )
        embed.add_field(
            name="📋 Comment ça marche ?",
            value="1️⃣ Cliquez sur le bouton\n"
                  "2️⃣ Un salon privé sera créé\n"
                  "3️⃣ Expliquez votre problème\n"
                  "4️⃣ Fermez le ticket quand c'est résolu",
            inline=False
        )
        
        view = TicketButton()
        
        await channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(
            f"{Emojis.SUCCESS} Système de tickets configuré dans {channel.mention}",
            ephemeral=True
        )
        
        logger.info(f"{interaction.user} a configuré le système de tickets dans #{channel.name}")
    
    # ===== CLOSE =====
    @app_commands.command(name="close", description="Fermer un ticket (retire l'accès aux non-mods)")
    @app_commands.describe(reason="Raison de la fermeture")
    async def close_ticket(self, interaction: discord.Interaction, reason: str = None):
        """Ferme le ticket actuel (étape 1)"""
        # Vérifier si c'est un salon de ticket
        ticket = await database.get_ticket(interaction.channel.id)
        
        if not ticket:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Cette commande ne peut être utilisée que dans un ticket.",
                ephemeral=True
            )
        
        if ticket['status'] == 'closed':
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Ce ticket est déjà fermé.",
                ephemeral=True
            )
        
        # Vérifier les permissions
        if not (interaction.user.guild_permissions.manage_channels or interaction.user.id == ticket['user_id']):
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Seul le créateur du ticket ou un modérateur peut le fermer.",
                ephemeral=True
            )
        
        await interaction.response.defer()
        
        # Marquer comme fermé
        await database.close_ticket(interaction.channel.id)
        
        # Retirer l'accès au créateur du ticket
        creator = interaction.guild.get_member(ticket['user_id'])
        if creator:
            await interaction.channel.set_permissions(
                creator,
                read_messages=False,
                send_messages=False
            )
        
        # Renommer le canal pour indiquer qu'il est fermé
        new_name = f"closed-{interaction.channel.name}" if not interaction.channel.name.startswith("closed-") else interaction.channel.name
        await interaction.channel.edit(name=new_name)
        
        # Message de fermeture
        embed = discord.Embed(
            title=f"{Emojis.LOCK} Ticket Fermé",
            description=f"Ce ticket a été fermé par {interaction.user.mention}\n\n"
                       f"Le ticket reste accessible aux modérateurs.\n"
                       f"Utilisez `/delete` ou le bouton ci-dessous pour le supprimer définitivement.",
            color=Colors.WARNING
        )
        
        if reason:
            embed.add_field(name="Raison", value=reason, inline=False)
        
        # Bouton de suppression
        delete_view = View(timeout=None)
        delete_button = Button(
            label="Supprimer le Ticket",
            style=discord.ButtonStyle.danger,
            emoji="🗑️",
            custom_id=f"delete_ticket_{interaction.channel.id}"
        )
        
        async def delete_callback(inter: discord.Interaction):
            if not inter.user.guild_permissions.manage_channels:
                return await inter.response.send_message(
                    f"{Emojis.ERROR} Seuls les modérateurs peuvent supprimer un ticket.",
                    ephemeral=True
                )
            
            await inter.response.send_message(
                f"{Emojis.LOADING} Suppression du ticket...",
                ephemeral=True
            )
            await interaction.channel.delete(reason=f"Ticket supprimé par {inter.user}")
        
        delete_button.callback = delete_callback
        delete_view.add_item(delete_button)
        
        await interaction.channel.send(embed=embed, view=delete_view)
        
        logger.info(f"Ticket {interaction.channel.name} fermé par {interaction.user}")
    
    # ===== DELETE =====
    @app_commands.command(name="delete", description="Supprimer définitivement un ticket fermé")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def delete_ticket(self, interaction: discord.Interaction):
        """Supprime définitivement un ticket (étape 2)"""
        # Vérifier si c'est un salon de ticket
        ticket = await database.get_ticket(interaction.channel.id)
        
        if not ticket:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Cette commande ne peut être utilisée que dans un ticket.",
                ephemeral=True
            )
        
        if ticket['status'] != 'closed':
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Le ticket doit être fermé avant d'être supprimé. Utilisez `/close` d'abord.",
                ephemeral=True
            )
        
        await interaction.response.send_message(
            f"{Emojis.LOADING} Suppression du ticket...",
            ephemeral=True
        )
        
        logger.info(f"Ticket {interaction.channel.name} supprimé par {interaction.user}")
        
        await interaction.channel.delete(reason=f"Ticket supprimé par {interaction.user}")
    
    # ===== ADD =====
    @app_commands.command(name="add", description="Ajouter un membre au ticket")
    @app_commands.describe(member="Le membre à ajouter")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def add_to_ticket(self, interaction: discord.Interaction, member: discord.Member):
        """Ajoute un membre au ticket"""
        ticket = await database.get_ticket(interaction.channel.id)
        
        if not ticket:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Cette commande ne peut être utilisée que dans un ticket.",
                ephemeral=True
            )
        
        await interaction.channel.set_permissions(
            member,
            read_messages=True,
            send_messages=True
        )
        
        embed = discord.Embed(
            description=f"{Emojis.SUCCESS} {member.mention} a été ajouté au ticket.",
            color=Colors.SUCCESS
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"{interaction.user} a ajouté {member} au ticket {interaction.channel.name}")
    
    # ===== REMOVE =====
    @app_commands.command(name="remove", description="Retirer un membre du ticket")
    @app_commands.describe(member="Le membre à retirer")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def remove_from_ticket(self, interaction: discord.Interaction, member: discord.Member):
        """Retire un membre du ticket"""
        ticket = await database.get_ticket(interaction.channel.id)
        
        if not ticket:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Cette commande ne peut être utilisée que dans un ticket.",
                ephemeral=True
            )
        
        await interaction.channel.set_permissions(member, overwrite=None)
        
        embed = discord.Embed(
            description=f"{Emojis.SUCCESS} {member.mention} a été retiré du ticket.",
            color=Colors.SUCCESS
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"{interaction.user} a retiré {member} du ticket {interaction.channel.name}")

async def setup(bot):
    await bot.add_cog(Tickets(bot))
