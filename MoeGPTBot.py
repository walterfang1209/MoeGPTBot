import json
import sys
from winsound import PlaySound
from ChatBot import ChatBot
from translateBaidu import translate_baidu
from tools import *
import os
import datetime
from termcolor import colored
from azure_speech import playSoundWithAzure
import voice_generator
from voice_generator import load_model, generateSound
import configparser
import Config

record_path = "./chat_record/"
character_path = "./characters/"

def get_input():
    print(">>>", end='')
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_input = input() + f'\n[系统时间: {time}]'
    sys.stdout.write('\r' + '信息正在飞快传往异次元...')
    sys.stdout.flush()
    return user_input

if __name__ == "__main__":
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    Config.checkApi(config)
    model_id = Config.choseLang(config)
    system_prompt, char_name = Config.choseChar()
    id, key = Config.getModel(model_id)

    global chinese_model_path
    global japanese_model_path
    if model_id == 0:
        voice_generator.chinese_model_path += key + '/' + key + '.pth'
    elif model_id == 1:
        voice_generator.japanese_model_path += key + '/' + key + '.pth'
    if 'zh' not in key:
        load_model(model_id)

    # 检查历史记录
    clear = False
    if not os.path.exists(record_path):
        os.mkdir(record_path)
    save_path = record_path
    emb_path = record_path + char_name + '.csv'
    record_path += char_name + '.json'
    if os.path.exists(record_path):
        print(colored('检查到历史记录存在，是否继续使用？(y/n)', 'green'),)
        load_record = input('>>>')
        if load_record == 'n':
            os.remove(record_path)
            if os.path.exists(emb_path):
                os.remove(emb_path)
        else:
            os.system('cls')
            clear = True
            with open(record_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                for item in messages:
                    if item['role'] == 'user':
                        print('>>>' + item['content'])
                    elif item['role'] == 'assistant':
                        print(item['content'])

    if not os.path.exists(record_path):
        name = input(f'{char_name}取一个名字吧: ')
        system_prompt += 'Your name is ' + name + '.'

    gpt = ChatBot(api_key=config.get('API', 'openai_key'),
                  prompt=system_prompt,
                  save_path=save_path,
                  file_name=char_name)
    gpt.cal_emb_from_file('./memory/' + char_name + '.txt')

    input('输入任意键开始...')

    if not clear:
        os.system('cls')

    while True:
        if model_id == 0:
            answer = gpt.ask(get_input()).replace('\n','')
            if 'zh-CN' in key:
                sys.stdout.write('\r' + ' '*50 + '\r')
                print(answer, flush=True)
                playSoundWithAzure(key, brackets_delete(answer))
            else:
                generateSound('[ZH]' + brackets_delete(answer) + '[ZH]', id)
                sys.stdout.write('\r' + ' '*50 + '\r')
                print(answer, flush=True)
                PlaySound(r'.\output.wav', flags=1)
        elif model_id == 1:
            answer = gpt.ask(get_input()).replace('\n','')
            trans = translate_baidu(brackets_delete(answer), config.get('API', 'baidu_appid'), config.get('API', 'baidu_secretKey'))
            if trans == None:
                print(colored('错误: 翻译 API 错误！', 'red'))
            generateSound(trans, id)
            sys.stdout.write('\r' + ' '*50 + '\r')
            print(answer, flush=True)
            PlaySound(r'.\output.wav', flags=1)