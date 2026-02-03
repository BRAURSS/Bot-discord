"""
Cog de Modération - Commandes de modération du serveur
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
import database
from config import Colors, Emojis
import logging

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    """Commandes de modération pour gérer le serveur"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # ===== BAN =====
    @app_commands.command(name="ban", description="Bannir un membre du serveur")
    @app_commands.describe(
        member="Le membre à bannir",
        reason="Raison du bannissement",
        delete_messages="Supprimer les messages (jours)"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member, 
        reason: str = "Aucune raison fournie",
        delete_messages: int = 0
    ):
        """Bannit un membre du serveur"""
        # Vérifier la hiérarchie des rôles (sauf pour le propriétaire du serveur)
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Vous ne pouvez pas bannir ce membre (rôle supérieur ou égal).",
                ephemeral=True
            )
        
        try:
            await member.ban(
                reason=f"{reason} | Par {interaction.user}",
                delete_message_days=delete_messages
            )
            
            # Log dans la base de données
            await database.add_mod_log(
                interaction.guild.id,
                "BAN",
                interaction.user.id,
                member.id,
                reason
            )
            
            # Envoyer au canal de logs
            log_embed = discord.Embed(
                title=f"{Emojis.BAN} Bannissement",
                color=Colors.ERROR,
                timestamp=discord.utils.utcnow()
            )
            log_embed.add_field(name="Membre", value=f"{member.mention} ({member.id})", inline=True)
            log_embed.add_field(name="Modérateur", value=f"{interaction.user.mention}", inline=True)
            log_embed.add_field(name="Raison", value=reason, inline=False)
            await database.send_mod_log(self.bot, interaction.guild.id, log_embed)
            
            # Embed de confirmation
            embed = discord.Embed(
                title=f"{Emojis.BAN} Membre banni",
                description=f"**{member.mention}** a été banni du serveur.",
                color=Colors.ERROR
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"ID: {member.id}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a banni {member} pour: {reason}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de bannir ce membre.",
                ephemeral=True
            )
    
    # ===== UNBAN =====
    @app_commands.command(name="unban", description="Débannir un utilisateur")
    @app_commands.describe(
        user_id="L'ID de l'utilisateur à débannir",
        reason="Raison du débannissement"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(
        self, 
        interaction: discord.Interaction, 
        user_id: str,
        reason: str = "Aucune raison fournie"
    ):
        """Débannit un utilisateur du serveur"""
        try:
            # Convertir l'ID en entier
            user_id_int = int(user_id)
            
            # Créer un objet User à partir de l'ID
            user = await self.bot.fetch_user(user_id_int)
            
            # Débannir l'utilisateur
            await interaction.guild.unban(
                user,
                reason=f"{reason} | Par {interaction.user}"
            )
            
            # Log dans la base de données
            await database.add_mod_log(
                interaction.guild.id,
                "UNBAN",
                interaction.user.id,
                user.id,
                reason
            )
            
            # Embed de confirmation
            embed = discord.Embed(
                title=f"{Emojis.SUCCESS} Utilisateur débanni",
                description=f"**{user.name}** (ID: {user.id}) a été débanni du serveur.",
                color=Colors.SUCCESS
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"ID: {user.id}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a débanni {user} pour: {reason}")
            
        except ValueError:
            await interaction.response.send_message(
                f"{Emojis.ERROR} L'ID fourni n'est pas valide. Veuillez fournir un ID Discord numérique.",
                ephemeral=True
            )
        except discord.NotFound:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Aucun bannissement trouvé pour cet ID.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de débannir cet utilisateur.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Une erreur s'est produite: {str(e)}",
                ephemeral=True
            )
            logger.error(f"Erreur lors du unban: {e}")
    
    # ===== TEMPBAN =====
    @app_commands.command(name="tempban", description="Bannir temporairement un utilisateur")
    @app_commands.describe(
        member="Le membre à bannir temporairement",
        duration="Durée (ex: 1h, 1d, 1w)",
        reason="Raison du bannissement",
        delete_messages="Supprimer les messages (jours)"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def tempban(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        duration: str,
        reason: str = "Aucune raison fournie",
        delete_messages: int = 0
    ):
        """Bannit temporairement un membre du serveur"""
        # Vérifier la hiérarchie des rôles (sauf pour le propriétaire du serveur)
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Vous ne pouvez pas bannir ce membre (rôle supérieur ou égal).",
                ephemeral=True
            )
        
        # Parser la durée
        from datetime import datetime, timedelta
        try:
            duration_seconds = self._parse_duration(duration)
            if duration_seconds is None:
                return await interaction.response.send_message(
                    f"{Emojis.ERROR} Format de durée invalide. Utilisez 1h, 1d, 1w, etc.",
                    ephemeral=True
                )
            
            expires_at = datetime.now() + timedelta(seconds=duration_seconds)
            
        except ValueError:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Format de durée invalide. Utilisez 1h, 1d, 1w, etc.",
                ephemeral=True
            )
        
        try:
            # Bannir le membre
            await member.ban(
                reason=f"{reason} | Par {interaction.user} | Temporaire jusqu'à {expires_at.strftime('%Y-%m-%d %H:%M')}",
                delete_message_days=delete_messages
            )
            
            # Enregistrer dans la base de données
            await database.add_temp_action(
                interaction.guild.id,
                member.id,
                "TEMPBAN",
                interaction.user.id,
                expires_at,
                reason
            )
            
            # Log dans la base de données
            await database.add_mod_log(
                interaction.guild.id,
                "TEMPBAN",
                interaction.user.id,
                member.id,
                f"{reason} | Durée: {duration}"
            )
            
            # Embed de confirmation
            embed = discord.Embed(
                title=f"{Emojis.BAN} Membre banni temporairement",
                description=f"**{member.mention}** a été banni du serveur.",
                color=Colors.ERROR
            )
            embed.add_field(name="Durée", value=duration, inline=True)
            embed.add_field(name="Expire le", value=expires_at.strftime("%Y-%m-%d %H:%M"), inline=True)
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"ID: {member.id} | Auto-unban activé")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a tempban {member} pour {duration}: {reason}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de bannir ce membre.",
                ephemeral=True
            )
    
    # ===== TEMPMUTE =====
    @app_commands.command(name="tempmute", description="Mute temporairement un membre")
    @app_commands.describe(
        member="Le membre à mute",
        duration="Durée (ex: 1h, 30m, 1d)",
        reason="Raison du mute"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def tempmute(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        duration: str,
        reason: str = "Aucune raison fournie"
    ):
        """Mute temporairement un membre (avec auto-unmute)"""
        # Vérifier la hiérarchie des rôles (sauf pour le propriétaire du serveur)
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Vous ne pouvez pas mute ce membre (rôle supérieur ou égal).",
                ephemeral=True
            )
        
        # Parser la durée
        from datetime import datetime, timedelta
        try:
            duration_seconds = self._parse_duration(duration)
            if duration_seconds is None or duration_seconds > 40320 * 60:  # Max 28 jours
                return await interaction.response.send_message(
                    f"{Emojis.ERROR} Format invalide ou durée trop longue (max 28 jours).",
                    ephemeral=True
                )
            
            expires_at = datetime.now() + timedelta(seconds=duration_seconds)
            
        except ValueError:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Format de durée invalide. Utilisez 1h, 30m, 1d, etc.",
                ephemeral=True
            )
        
        try:
            # Mute le membre
            await member.timeout(
                timedelta(seconds=duration_seconds),
                reason=f"{reason} | Par {interaction.user} | Temporaire jusqu'à {expires_at.strftime('%Y-%m-%d %H:%M')}"
            )
            
            # Enregistrer dans la base de données pour tracking
            await database.add_temp_action(
                interaction.guild.id,
                member.id,
                "TEMPMUTE",
                interaction.user.id,
                expires_at,
                reason
            )
            
            # Log dans la base de données
            await database.add_mod_log(
                interaction.guild.id,
                "TEMPMUTE",
                interaction.user.id,
                member.id,
                f"{reason} | Durée: {duration}"
            )
            
            # Embed de confirmation
            embed = discord.Embed(
                title=f"{Emojis.MUTE} Membre mute temporairement",
                description=f"**{member.mention}** a été mis en sourdine.",
                color=Colors.WARNING
            )
            embed.add_field(name="Durée", value=duration, inline=True)
            embed.add_field(name="Expire le", value=expires_at.strftime("%Y-%m-%d %H:%M"), inline=True)
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"Discord gère l'auto-unmute")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a tempmute {member} pour {duration}: {reason}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de mute ce membre.",
                ephemeral=True
            )
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse une chaîne de durée (1h, 1d, 1w) en secondes"""
        import re
        
        pattern = r'(\d+)([smhdw])'
        matches = re.findall(pattern, duration_str.lower())
        
        if not matches:
            return None
        
        total_seconds = 0
        for amount, unit in matches:
            amount = int(amount)
            if unit == 's':
                total_seconds += amount
            elif unit == 'm':
                total_seconds += amount * 60
            elif unit == 'h':
                total_seconds += amount * 3600
            elif unit == 'd':
                total_seconds += amount * 86400
            elif unit == 'w':
                total_seconds += amount * 604800
        
        return total_seconds if total_seconds > 0 else None
    
    # ===== KICK =====
    @app_commands.command(name="kick", description="Expulser un membre du serveur")
    @app_commands.describe(
        member="Le membre à expulser",
        reason="Raison de l'expulsion"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member, 
        reason: str = "Aucune raison fournie"
    ):
        """Expulse un membre du serveur"""
        # Vérifier la hiérarchie des rôles (sauf pour le propriétaire du serveur)
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Vous ne pouvez pas expulser ce membre (rôle supérieur ou égal).",
                ephemeral=True
            )
        
        try:
            await member.kick(reason=f"{reason} | Par {interaction.user}")
            
            await database.add_mod_log(
                interaction.guild.id,
                "KICK",
                interaction.user.id,
                member.id,
                reason
            )
            
            embed = discord.Embed(
                title=f"{Emojis.KICK} Membre expulsé",
                description=f"**{member.mention}** a été expulsé du serveur.",
                color=Colors.WARNING
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"ID: {member.id}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a expulsé {member} pour: {reason}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission d'expulser ce membre.",
                ephemeral=True
            )
    
    # ===== MUTE (TIMEOUT) =====
    @app_commands.command(name="mute", description="Mettre un membre en sourdine (timeout)")
    @app_commands.describe(
        member="Le membre à mute",
        duration="Durée en minutes",
        reason="Raison du mute"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        duration: int,
        reason: str = "Aucune raison fournie"
    ):
        """Met un membre en timeout"""
        # Vérifier la hiérarchie des rôles (sauf pour le propriétaire du serveur)
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Vous ne pouvez pas mute ce membre (rôle supérieur ou égal).",
                ephemeral=True
            )
        
        if duration > 40320:  # Max 28 jours
            return await interaction.response.send_message(
                f"{Emojis.ERROR} La durée maximale est de 28 jours (40320 minutes).",
                ephemeral=True
            )
        
        try:
            await member.timeout(
                timedelta(minutes=duration),
                reason=f"{reason} | Par {interaction.user}"
            )
            
            await database.add_mod_log(
                interaction.guild.id,
                "MUTE",
                interaction.user.id,
                member.id,
                f"{reason} | Durée: {duration}min"
            )
            
            embed = discord.Embed(
                title=f"{Emojis.MUTE} Membre mute",
                description=f"**{member.mention}** a été mis en sourdine.",
                color=Colors.WARNING
            )
            embed.add_field(name="Durée", value=f"{duration} minutes", inline=True)
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a mute {member} pour {duration}min: {reason}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de mute ce membre.",
                ephemeral=True
            )
    
    # ===== UNMUTE =====
    @app_commands.command(name="unmute", description="Retirer la sourdine d'un membre")
    @app_commands.describe(member="Le membre à unmute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        """Retire le timeout d'un membre"""
        try:
            await member.timeout(None, reason=f"Unmute par {interaction.user}")
            
            await database.add_mod_log(
                interaction.guild.id,
                "UNMUTE",
                interaction.user.id,
                member.id,
                None
            )
            
            embed = discord.Embed(
                title=f"{Emojis.UNMUTE} Membre unmute",
                description=f"**{member.mention}** peut à nouveau parler.",
                color=Colors.SUCCESS
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a unmute {member}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de unmute ce membre.",
                ephemeral=True
            )
    
    # ===== WARN =====
    @app_commands.command(name="warn", description="Avertir un membre")
    @app_commands.describe(
        member="Le membre à avertir",
        reason="Raison de l'avertissement"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member, 
        reason: str = "Aucune raison fournie"
    ):
        """Avertit un membre"""
        await database.add_warn(
            interaction.guild.id,
            member.id,
            interaction.user.id,
            reason
        )
        
        warn_count = await database.get_warn_count(interaction.guild.id, member.id)
        
        embed = discord.Embed(
            title=f"{Emojis.WARN} Avertissement",
            description=f"**{member.mention}** a reçu un avertissement.",
            color=Colors.WARNING
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.add_field(name="Total d'avertissements", value=f"{warn_count}", inline=True)
        embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
        # Envoyer un DM au membre
        try:
            dm_embed = discord.Embed(
                title=f"{Emojis.WARN} Vous avez reçu un avertissement",
                description=f"Serveur: **{interaction.guild.name}**",
                color=Colors.WARNING
            )
            dm_embed.add_field(name="Raison", value=reason, inline=False)
            dm_embed.add_field(name="Total", value=f"{warn_count} avertissement(s)", inline=True)
            await member.send(embed=dm_embed)
        except:
            pass  # L'utilisateur a peut-être désactivé les DMs
        
        logger.info(f"{interaction.user} a averti {member}: {reason}")
    
    # ===== WARNINGS =====
    @app_commands.command(name="warnings", description="Voir les avertissements d'un membre")
    @app_commands.describe(member="Le membre à vérifier")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        """Affiche les avertissements d'un membre"""
        warns = await database.get_warns(interaction.guild.id, member.id)
        
        if not warns:
            return await interaction.response.send_message(
                f"{Emojis.SUCCESS} **{member.display_name}** n'a aucun avertissement.",
                ephemeral=True
            )
        
        embed = discord.Embed(
            title=f"Avertissements de {member.display_name}",
            description=f"Total: **{len(warns)}** avertissement(s)",
            color=Colors.INFO
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        for i, warn in enumerate(warns[:10], 1):  # Max 10 derniers warns
            moderator = interaction.guild.get_member(warn['moderator_id'])
            mod_name = moderator.mention if moderator else f"ID: {warn['moderator_id']}"
            
            embed.add_field(
                name=f"#{i} - {warn['timestamp'][:10]}",
                value=f"**Raison:** {warn['reason'] or 'Aucune'}\n**Par:** {mod_name}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ===== CLEAR/PURGE =====
    @app_commands.command(name="clear", description="Supprimer des messages")
    @app_commands.describe(amount="Nombre de messages à supprimer (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        """Supprime des messages en masse"""
        if amount < 1 or amount > 100:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Veuillez spécifier un nombre entre 1 et 100.",
                ephemeral=True
            )
        
        await interaction.response.defer(ephemeral=True)
        
        deleted = await interaction.channel.purge(limit=amount)
        
        await database.add_mod_log(
            interaction.guild.id,
            "CLEAR",
            interaction.user.id,
            interaction.channel.id,
            f"{len(deleted)} messages supprimés"
        )
        
        await interaction.followup.send(
            f"{Emojis.SUCCESS} **{len(deleted)}** message(s) supprimé(s).",
            ephemeral=True
        )
        logger.info(f"{interaction.user} a supprimé {len(deleted)} messages dans #{interaction.channel.name}")
    
    # ===== BANS LIST =====
    @app_commands.command(name="bans", description="Liste des utilisateurs bannis du serveur")
    @app_commands.describe(page="Numéro de page (optionnel)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def bans(self, interaction: discord.Interaction, page: int = 1):
        """Affiche la liste paginée des bannissements"""
        await interaction.response.defer()
        
        try:
            # Récupérer tous les bans
            bans = [entry async for entry in interaction.guild.bans(limit=None)]
            
            if not bans:
                return await interaction.followup.send(
                    f"{Emojis.SUCCESS} Aucun utilisateur banni sur ce serveur.",
                    ephemeral=True
                )
            
            # Pagination
            per_page = 10
            total_pages = (len(bans) - 1) // per_page + 1
            page = max(1, min(page, total_pages))
            
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_bans = bans[start_idx:end_idx]
            
            # Créer l'embed
            embed = discord.Embed(
                title=f"📋 Liste des Bannissements",
                description=f"Total: **{len(bans)}** utilisateur(s) banni(s)",
                color=Colors.INFO
            )
            
            for entry in page_bans:
                user = entry.user
                reason = entry.reason or "Aucune raison fournie"
                embed.add_field(
                    name=f"{user.name} (ID: {user.id})",
                    value=f"**Raison:** {reason[:100]}{'...' if len(reason) > 100 else ''}",
                    inline=False
                )
            
            embed.set_footer(text=f"Page {page}/{total_pages}")
            
            # Créer les boutons de navigation si nécessaire
            if total_pages > 1:
                view = BanListView(page, total_pages, interaction.user.id)
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
                
            logger.info(f"{interaction.user} a consulté la liste des bans (page {page})")
            
        except discord.Forbidden:
            await interaction.followup.send(
                f"{Emojis.ERROR} Je n'ai pas la permission de voir les bannissements.",
                ephemeral=True
            )
    
    # ===== MASSBAN =====
    @app_commands.command(name="massban", description="Bannir plusieurs utilisateurs en même temps")
    @app_commands.describe(
        user_ids="Liste des IDs d'utilisateurs séparés par des espaces",
        reason="Raison du bannissement"
    )
    @app_commands.checks.has_permissions(ban_members=True, administrator=True)
    async def massban(
        self,
        interaction: discord.Interaction,
        user_ids: str,
        reason: str = "Aucune raison fournie"
    ):
        """Bannit plusieurs utilisateurs en même temps"""
        await interaction.response.defer()
        
        # Parser les IDs
        ids = user_ids.replace(',', ' ').split()
        valid_ids = []
        
        for id_str in ids:
            try:
                valid_ids.append(int(id_str.strip()))
            except ValueError:
                continue
        
        if not valid_ids:
            return await interaction.followup.send(
                f"{Emojis.ERROR} Aucun ID valide trouvé.",
                ephemeral=True
            )
        
        if len(valid_ids) > 50:
            return await interaction.followup.send(
                f"{Emojis.ERROR} Limite de 50 utilisateurs maximum par opération.",
                ephemeral=True
            )
        
        # Traiter les bans
        success_count = 0
        fail_count = 0
        
        for user_id in valid_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                await interaction.guild.ban(
                    user,
                    reason=f"[MASSBAN] {reason} | Par {interaction.user}"
                )
                
                await database.add_mod_log(
                    interaction.guild.id,
                    "MASSBAN",
                    interaction.user.id,
                    user_id,
                    reason
                )
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Erreur lors du massban de {user_id}: {e}")
                fail_count += 1
        
        # Résumé
        embed = discord.Embed(
            title=f"{Emojis.BAN} Massban Terminé",
            description=f"Opération de bannissement en masse effectuée.",
            color=Colors.ERROR
        )
        embed.add_field(name="✅ Succès", value=str(success_count), inline=True)
        embed.add_field(name="❌ Échecs", value=str(fail_count), inline=True)
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.set_footer(text=f"Modérateur: {interaction.user}")
        
        await interaction.followup.send(embed=embed)
        logger.info(f"{interaction.user} a massban {success_count} utilisateurs")
    
    # ===== MASSKICK =====
    @app_commands.command(name="masskick", description="Expulser plusieurs membres en même temps")
    @app_commands.describe(
        members="Mentionnez les membres séparés par des espaces",
        reason="Raison de l'expulsion"
    )
    @app_commands.checks.has_permissions(kick_members=True, administrator=True)
    async def masskick(
        self,
        interaction: discord.Interaction,
        members: str,
        reason: str = "Aucune raison fournie"
    ):
        """Expulse plusieurs membres en même temps"""
        await interaction.response.defer()
        
        # Parser les mentions
        import re
        user_ids = re.findall(r'<@!?(\d+)>', members)
        
        if not user_ids:
            return await interaction.followup.send(
                f"{Emojis.ERROR} Aucun membre mentionné. Utilisez @mention pour chaque membre.",
                ephemeral=True
            )
        
        if len(user_ids) > 30:
            return await interaction.followup.send(
                f"{Emojis.ERROR} Limite de 30 membres maximum par opération.",
                ephemeral=True
            )
        
        # Traiter les kicks
        success_count = 0
        fail_count = 0
        
        for user_id_str in user_ids:
            try:
                member = interaction.guild.get_member(int(user_id_str))
                if not member:
                    fail_count += 1
                    continue
                
                # Vérifier la hiérarchie
                if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
                    fail_count += 1
                    continue
                
                await member.kick(reason=f"[MASSKICK] {reason} | Par {interaction.user}")
                
                await database.add_mod_log(
                    interaction.guild.id,
                    "MASSKICK",
                    interaction.user.id,
                    member.id,
                    reason
                )
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Erreur lors du masskick de {user_id_str}: {e}")
                fail_count += 1
        
        # Résumé
        embed = discord.Embed(
            title=f"{Emojis.KICK} Masskick Terminé",
            description=f"Opération d'expulsion en masse effectuée.",
            color=Colors.WARNING
        )
        embed.add_field(name="✅ Succès", value=str(success_count), inline=True)
        embed.add_field(name="❌ Échecs", value=str(fail_count), inline=True)
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.set_footer(text=f"Modérateur: {interaction.user}")
        
        await interaction.followup.send(embed=embed)
        logger.info(f"{interaction.user} a masskick {success_count} membres")

# ===== Vue pour pagination des bans =====
class BanListView(discord.ui.View):
    """Vue avec boutons de navigation pour la liste des bans"""
    
    def __init__(self, current_page: int, total_pages: int, author_id: int):
        super().__init__(timeout=180)
        self.current_page = current_page
        self.total_pages = total_pages
        self.author_id = author_id
        
        # Désactiver les boutons si nécessaire
        if current_page <= 1:
            self.previous_button.disabled = True
        if current_page >= total_pages:
            self.next_button.disabled = True
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifier que seul l'auteur peut utiliser les boutons"""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Seul l'auteur de la commande peut utiliser ces boutons.",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(label="◀️ Précédent", style=discord.ButtonStyle.gray)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Aller à la page précédente"""
        await interaction.response.defer()
        
        new_page = self.current_page - 1
        if new_page < 1:
            return
        
        # Re-exécuter la commande avec la nouvelle page
        from discord.ext.commands import Bot
        bot: Bot = interaction.client
        moderation_cog = bot.get_cog("Moderation")
        
        if moderation_cog:
            await moderation_cog.bans.callback(moderation_cog, interaction, page=new_page)
    
    @discord.ui.button(label="▶️ Suivant", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Aller à la page suivante"""
        await interaction.response.defer()
        
        new_page = self.current_page + 1
        if new_page > self.total_pages:
            return
        
        # Re-exécuter la commande avec la nouvelle page
        from discord.ext.commands import Bot
        bot: Bot = interaction.client
        moderation_cog = bot.get_cog("Moderation")
        
        if moderation_cog:
            await moderation_cog.bans.callback(moderation_cog, interaction, page=new_page)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
