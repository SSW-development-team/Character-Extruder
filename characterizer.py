import os
from sre_constants import ANY
from string import Template
import ClauseWizard
from CountryLeader import CountryLeader
from IdeologyLeader import IdeologyLeader

# キャラクターデータ抽出ツール
# 1. 読み込むhoi4ファイル, キャラクターフォルダを指定する
INPUT_FILE = R"C:\Users\YsikiShokurin\Programming\SSW_mod\history\countries\ANG - Angola.txt"
CHARACTER_DIR = R"C:\Users\YsikiShokurin\Programming\SSW_mod\common\characters"
# 2. このファイルを実行
# 3. 読み込んだファイルの中身をoutput.txtで置き換える
# 4. out_chara.txtをcharactersフォルダに配置する


def countryTagIdentifier(filename: str):
    name = filename.split("\\")[-1].split(".")[0]
    nameparts: list[str] = [*name.split("_"), *name.split(" - ")]
    for part in nameparts:
        if part.isupper():
            return part


def extruder(token: list[str]):
    """return the list of CountryLeader from tokens"""
    l_characters: dict[str, CountryLeader] = dict()
    # TARGET_SINGLE_TOKENS = ["picture", "expire", "ideology"]
    while len(token) > 0:
        tokenpair = token.pop(0)
        if type(tokenpair) != list or len(tokenpair) == 1:  # トークンが長さ2のリストでない場合
            continue  # 解析せずスキップ
        key, value = tokenpair
        if key == "create_country_leader":
            country_leader_id: str = None
            current_ideology = ""
            expire_value_unknown_ideology = ""
            for subkey, subvalue in value:
                if subkey == "name":
                    name = subvalue[0]
                    country_leader_id = tag+"_"+name.lower().replace(" ", "_")
                    chara = l_characters.get(
                        country_leader_id, CountryLeader(country_leader_id))
                    chara.name = name
                    l_characters[country_leader_id] = chara
                elif subkey == "picture":
                    picture = subvalue[0].replace(
                        r"^\"|\"$", "")  # 先頭と末尾のクオーテーションは除く
                    chara = l_characters[country_leader_id]
                    if chara == None:
                        Exception(
                            "name token was not found before other token apper")
                    chara.picture = picture
                elif subkey == "expire":
                    expire = subvalue[0]
                    expire_value_unknown_ideology = expire
                elif subkey == "ideology":
                    ideology = subvalue[0]
                    current_ideology = ideology
                    chara = l_characters[country_leader_id]
                    if chara == None:
                        Exception(
                            "name token was not found before other token apper")
                    ideology_leader = chara.ideologies.get(
                        ideology, IdeologyLeader(ideology))
                    ideology_leader.expire = expire_value_unknown_ideology
                    chara.ideologies[ideology] = ideology_leader
                elif subkey == "traits":
                    traits: ANY = subvalue
                    if type(traits[0]) == list:
                        traits = [trait[0] for trait in traits]
                    chara = l_characters[country_leader_id]
                    if chara == None:
                        Exception(
                            "name token was not found before other token apper")
                    chara.ideologies[current_ideology].traits = traits
        else:  # トークンがcreate_country_leaderでない場合
            # 値を解析予定トークンとして追加してネストを深くする
            token.extend(value)
    return l_characters


def splitter(string: str):
    """長過ぎるファイルのコンテンツを、複数回改行が連続したところで区切ります"""
    return string.split("\ncountry_even")


def getTemplate(filename: str):
    f = open(filename, "r", encoding="utf-8")
    template = "\n".join(f.readlines())
    f.close()
    return template


os.chdir(os.getcwd())

mode = "replace"
tag = countryTagIdentifier(INPUT_FILE)
if tag == None:
    print("カントリータグを判別できませんでした。実行ファイル下のフォルダに結果を出力します。")
    mode = "non-replace"
    tag = "TAG_REPLACE"

raw_txt = getTemplate(INPUT_FILE)
output_path = f"output/ssw_{tag}.txt" if mode != "replace" else INPUT_FILE
os.makedirs("output", exist_ok=True)
out_file = open(output_path, "w", encoding="utf-8")
chara_path = f"characters/ssw_{tag}.txt" if mode != "replace" else CHARACTER_DIR+f"\ssw_{tag}.txt"
os.makedirs("characters", exist_ok=True)
chara_file = open(chara_path, "a", encoding="utf-8")

ideology_template = getTemplate("templates/ideology.txt")
character_template = getTemplate("templates/character.txt")
root_template = getTemplate("templates/root.txt")

output = []
nest_count = 0
tokens_2_parse = ""
characters: dict[str, CountryLeader] = dict()


for line in raw_txt.splitlines():
    if "create_country_leader" in line:
        nest_count += 1
    elif 0 < nest_count and "{" in line:
        nest_count += 1
    if nest_count == 0:
        output.append(line+"\n")
    if 0 < nest_count and "}" in line:
        nest_count -= 1
    if nest_count > 0:
        tokens_2_parse += line+"\n"
    elif tokens_2_parse != "":
        tokens_2_parse += "}"
        token = ClauseWizard.cwparse(tokens_2_parse)
        characters_local = extruder(token)
        # print(characters_local)
        for chara_key in characters_local:  # グローバル辞書にすでにキャラが登録されている場合、まるごと上書きされるのを避ける
            global_chara = characters.get(chara_key)
            if global_chara == None:
                characters[chara_key] = characters_local[chara_key]
            else:  # すでにキャラが登録されている場合は、イデオロギー情報のみを追加
                global_chara.ideologies.update(
                    characters_local[chara_key].ideologies)
        tokens_2_parse = ""
        output.extend(
            [f"recruit_character = {key}\n" for key in characters_local.keys()])

out_file.writelines(output)
out_file.close()

# 出力整形
character_txt = ""
for key in characters:
    chara = characters[key]
    ideology_txt = ""
    for ideology_id in chara.ideologies:
        ideology_data = chara.ideologies[ideology_id]
        replacer = {"ideology": ideology_id,
                    "expire": ideology_data.expire, "traits": "\n".join(ideology_data.traits)}
        ideology_txt += Template(ideology_template).substitute(replacer)
    replacer = {"id": chara.id,
                "picture": chara.picture, "ideology_leaders": ideology_txt}
    character_txt += Template(character_template).substitute(replacer)
replacer = {"characters": character_txt}
root_txt = Template(root_template).substitute(replacer)

chara_file.write(root_txt)
chara_file.close()

print("実行が終了しました")
