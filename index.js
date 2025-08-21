const { Client, GatewayIntentBits } = require('discord.js');
const { joinVoiceChannel, createAudioPlayer, createAudioResource, AudioPlayerStatus } = require('@discordjs/voice');
const ytdl = require('ytdl-core');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

const TOKEN = 'MTQwMDYzMTk2ODQ5MTg5Njg5MgGO-2JFNfDZB8apjt pKHc1QG8p-elYs0aSlitz09pP60'; // ここを自分のトークンに書き換える

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

client.on('messageCreate', async (message) => {
  if (!message.guild) return;
  // コマンド例: !play https://www.youtube.com/watch?v=xxxxxxxxxxx
  if (message.content.startsWith('!play ')) {
    const url = message.content.split(' ')[1];
    if (!ytdl.validateURL(url)) {
      message.reply('無効なYouTubeリンクです。');
      return;
    }
if (message.member.voice.channel) {
      const connection = joinVoiceChannel({
        channelId: message.member.voice.channel.id,
        guildId: message.guild.id,
        adapterCreator: message.guild.voiceAdapterCreator,
      });

      const stream = ytdl(url, { filter: 'audioonly' });
      const resource = createAudioResource(stream);
      const player = createAudioPlayer();

      player.play(resource);
      connection.subscribe(player);

      message.reply('再生を開始します。');

      player.on(AudioPlayerStatus.Idle, () => {
        connection.destroy();
      });

      player.on('error', error => {
console.error(error);
        message.reply('再生中にエラーが発生しました。');
        connection.destroy();
      });
    } else {
      message.reply('ボイスチャンネルに参加してください。');
    }
  }
});

client.login(TOKEN);
