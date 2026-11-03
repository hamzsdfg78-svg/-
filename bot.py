import discord
from discord import app_commands

# إعدادات البوت والـ Intents الأساسية
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # مزامنة أوامر السلاش مع ديسكورد
        await self.tree.sync()
        print("تم مزامنة أوامر السلاش بنجاح!")

client = MyBot()

@client.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {client.user}")

# تعريف أمر السلاش الشامل /manage لإدارة الرومات والرتب
@client.tree.command(name="manage", description="إدارة شاملة لإنشاء أو حذف الرومات والرتب دفعة واحدة")
@app_commands.choices(action=[
    app_commands.Choice(name="إنشاء رومات", value="create_channels"),
    app_commands.Choice(name="حذف رومات بالاسم", value="delete_channels"),
    app_commands.Choice(name="إنشاء رتب", value="create_roles"),
    app_commands.Choice(name="حذف رتب بالاسم", value="delete_roles")
])
@app_commands.choices(type=[
    app_commands.Choice(name="نصي (Text)", value="text"),
    app_commands.Choice(name="صوتي (Voice)", value="voice")
])
@app_commands.describe(
    action="اختر العملية المطلوبة",
    name="اسم الروم أو الرتبة المراد إنشاؤها أو حذفها",
    count="العدد المطلوب (من 1 إلى 20)",
    type="نوع الروم (مطلوب فقط عند إنشاء الرومات)"
)
async def manage(interaction: discord.Interaction, action: str, name: str, count: int, type: str = None):
    # التحقق من أن العدد ضمن الحدود المسموحة
    if count < 1 or count > 20:
        await interaction.response.send_message("الرجاء اختيار عدد بين 1 و 20.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True, ephemeral=True)

    try:
        success_count = 0

        # 1. إنشاء الرومات
        if action == "create_channels":
            if not interaction.user.guild_permissions.manage_channels:
                return await interaction.edit_original_response(content="ما عندك صلاحية لإدارة الرومات!")
            if not type:
                return await interaction.edit_original_response(content="الرجاء تحديد نوع الروم (نصي أو صوتي)!")

            for i in range(1, count + 1):
                channel_name = f"{name}-{i}" if count > 1 else name
                if type == "text":
                    await interaction.guild.create_text_channel(channel_name)
                else:
                    await interaction.guild.create_voice_channel(channel_name)
                success_count += 1

            await interaction.edit_original_response(content=f"تم إنشاء **{success_count}** روم بنجاح باسم: **{name}**.")

        # 2. حذف الرومات المطابقة للأسماء
        elif action == "delete_channels":
            if not interaction.user.guild_permissions.manage_channels:
                return await interaction.edit_original_response(content="ما عندك صلاحية لإدارة الرومات!")

            channels = [c for c in interaction.guild.channels if name in c.name]
            if not channels:
                return await interaction.edit_original_response(content="لم يتم العثور على رومات تطابق هذا الاسم.")

            deleted = 0
            for channel in channels:
                if deleted >= count:
                    break
                await channel.delete()
                deleted += 1

            await interaction.edit_original_response(content=f"تم حذف **{deleted}** روم تطابق الاسم: **{name}**.")

        # 3. إنشاء الرتب
        elif action == "create_roles":
            if not interaction.user.guild_permissions.manage_roles:
                return await interaction.edit_original_response(content="ما عندك صلاحية لإدارة الرتب!")

            for i in range(1, count + 1):
                role_name = f"{name} {i}" if count > 1 else name
                await interaction.guild.create_role(name=role_name, reason="منشأة بواسطة البوت")
                success_count += 1

            await interaction.edit_original_response(content=f"تم إنشاء **{success_count}** رتبة بنجاح باسم: **{name}**.")

        # 4. حذف الرتب المطابقة للأسماء
        elif action == "delete_roles":
            if not interaction.user.guild_permissions.manage_roles:
                return await interaction.edit_original_response(content="ما عندك صلاحية لإدارة الرتب!")

            roles = [r for r in interaction.guild.roles if name in r.name and r != interaction.guild.default_role]
            if not roles:
                return await interaction.edit_original_response(content="لم يتم العثور على رتب تطابق هذا الاسم.")

            deleted = 0
            for role in roles:
                if deleted >= count:
                    break
                try:
                    await role.delete()
                    deleted += 1
                except:
                    pass

            await interaction.edit_original_response(content=f"تم حذف **{deleted}** رتبة تطابق الاسم: **{name}**.")

    except Exception as e:
        print(e)
        await interaction.edit_original_response(content="حدث خطأ أثناء تنفيذ الأمر، تأكد من صلاحيات البوت.")

# حط توكن بوتك هنا بدل الكلام اللي بين الأقواس
client.run("MTU2NzIyNzczMDM0NzU1NjkxNQ.GsjJz4.gJBO4SiSm5q3SU0PntF6FdVp9G81Sy8B5T-H44")
