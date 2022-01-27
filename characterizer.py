import os
from string import Template
import ClauseWizard

# キャラクターデータ抽出ツール
INPUT_FILE = "input.txt"  # 1. 読み込むhoi4ファイルを指定する
# 2. このファイルを実行
# 3. 読み込んだファイルの中身をoutput.txtで置き換える
# 4. out_chara.txtをcharactersフォルダに配置する


class IdeologyLeader():
    ideology = ""
    expire = ""
    traits: list[str] = []

    def __init__(self, ideology):
        self.ideology = ideology

    def __repr__(self):
        return f"[{self.expire}, {self.traits}]"


class CountryLeader():
    id = ""
    name = ""
    picture = ""
    ideologies: dict[str, IdeologyLeader] = dict()

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"{self.name}, {self.picture}, {self.ideologies}"


def extruder(token: list[str]):
    """return the list of CountryLeader from tokens"""
    characters: dict[str, CountryLeader] = dict()
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
                    country_leader_id = name.lower().replace(" ", "_")
                    chara = characters.get(
                        country_leader_id, CountryLeader(country_leader_id))
                    chara.name = name
                    characters[country_leader_id] = chara
                elif subkey == "picture":
                    picture = subvalue[0]
                    chara = characters[country_leader_id]
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
                    chara = characters[country_leader_id]
                    if chara == None:
                        Exception(
                            "name token was not found before other token apper")
                    ideology_leader = chara.ideologies.get(
                        ideology, IdeologyLeader(ideology))
                    ideology_leader.expire = expire_value_unknown_ideology
                    chara.ideologies[ideology] = ideology_leader
                elif subkey == "traits":
                    traits = subvalue
                    chara = characters[country_leader_id]
                    if chara == None:
                        Exception(
                            "name token was not found before other token apper")
                    chara.ideologies[current_ideology].traits = traits
        else:  # トークンがcreate_country_leaderでない場合
            # 値を解析予定トークンとして追加してネストを深くする
            token.extend(value)
    return characters


def splitter(string: str):
    """長過ぎるファイルのコンテンツを、複数回改行が連続したところで区切ります"""
    return string.split("\ncountry_even")


def getTemplate(filename: str):
    f = open(filename, "r", encoding="utf-8")
    template = "\n".join(f.readlines())
    f.close()
    return template


os.chdir(os.getcwd())

raw_txt = getTemplate(INPUT_FILE)
out_file = open("output.txt", "w", encoding="utf-8")
chara_file = open("out_chara.txt", "w", encoding="utf-8")

ideology_template = getTemplate("ideology.txt")
character_template = getTemplate("character.txt")
root_template = getTemplate("root.txt")

output = []
nest_count = 0
tokens_2_parse = ""
characters: dict[str, CountryLeader] = dict()


for line in raw_txt.splitlines():
    output.append(line+"\n")
    if "create_country_leader" in line:
        nest_count += 1
    elif 0 < nest_count and "{" in line:
        nest_count += 1
    elif 0 < nest_count and "}" in line:
        nest_count -= 1
    if nest_count > 0:
        tokens_2_parse += line+"\n"
    elif tokens_2_parse != "":
        tokens_2_parse += "}"
        token = ClauseWizard.cwparse(tokens_2_parse)
        characters_local = extruder(token)
        # print(characters_local)
        characters.update(characters_local)
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
