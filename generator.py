from langchain.agents import Tool, ZeroShotAgent, load_tools, AgentExecutor
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import StructuredTool
from langchain.utilities import ApifyWrapper, SerpAPIWrapper
from apify_client import ApifyClient
from dotenv import load_dotenv
import os


class ImagePromptGenerator:
    SETTINGS_PATHS = {
        "clothing": "./settings/clothing.txt",
        "background": "./settings/background.txt",
        "looks": "./settings/looks.txt",
        "composition": "./settings/composition.txt",
        "posture": "./settings/posture.txt"
    }

    def __init__(self):
        self.llm = OpenAI(model_name="gpt-4", temperature=0.7)
        self.APIFY_API_TOKEN = self._load_environment_variable("APIFY_API_TOKEN")
    
    @staticmethod
    def _load_environment_variable(variable_name):
        load_dotenv()
        return os.getenv(variable_name)

    @staticmethod
    def _read_prompt(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _instagram_search(self, tag):
        client = ApifyClient(self.APIFY_API_TOKEN)
        run_input = {
            "directUrls": [f"https://www.instagram.com/explore/tags/{tag}/"],
            "resultsType": "details",
            "resultsLimit": 5,
            "searchType": "hashtag",
            "searchLimit": 1,
        }
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)
        captions = [post["caption"] for item in client.dataset(run["defaultDatasetId"]).iterate_items() if "topPosts" in item for post in item["topPosts"] if "caption" in post]
        return captions
    
    def organize(self, magic_arg, situation_arg):
        """
        与えられた状況に適切な呪文になるように、最終的に呪文を整形するツール。
        """
        # Define Prompt for organize
        template_for_organize = self._read_prompt("/Users/cisvhat/sns-agent/settings/organize.txt")
        prompt_for_organize = PromptTemplate(
            input_variables=["situation", "magic"],
            template=template_for_organize
        )
        organize_chain = LLMChain(llm=self.llm, prompt=prompt_for_organize)
        return organize_chain.run({"situation": situation_arg, "magic": magic_arg})

    def parsing_organize(self, string):
        parts = string.split(",")
        situation_arg = parts[-1].strip()
        magic_arg = ",".join(parts[:-1]).strip()
        return self.organize(magic_arg, situation_arg)
    
    def execute_first_stage(self, person, situation):
        tools_for_thought = load_tools(["serpapi"])
        tools_for_thought.append(Tool(name="instagram search", func=self._instagram_search, description="インスタグラムを検索して、いろんな人のインスタグラムでの投稿内容が取得できます。投稿のアイディアを得たいときに参考になるので使ってください。検索クエリとなる、１単語だけ入力してください。"))

        # 服装、背景、人物の外見的特徴
        prefix = """以下に与えられた人物と状況に対して、あなたはんその人物になりきって思考し、その状況下で画像投稿SNSであるインスタグラムに投稿する写真について、どのような写真にするか考えてください。
        その人物になりきって、写真の強調部位、アングル、外見的特徴、服装、姿勢、背景など、具体的に説明してください。
        建物などを表す固有名詞が現れた場合、ツールを使って検索するなどして、固有名詞の表す建物の形状がどのようなものかが、誰にでも伝わるように詳細に説明するようにしてください。

        人物になりきって、次のツールを使いこなしてください:"""
        suffix = """
        では、以下の情報をもとに、推論を開始してください。
        人物: {person}
        状況: {situation}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools_for_thought,
            prefix=prefix,
            suffix=suffix,
            input_variables=["person", "situation", "agent_scratchpad"]
        )

        # LLMChainの準備
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)

        # エージェントの準備
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools_for_thought)
        agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools_for_thought, verbose=True)
        return agent_executor.run({"person": person, "situation": situation})

    def execute_second_stage(self, person, situation, agent_scratchpad):
        # Define the tools and agent's prompt
        tools_for_magic = []
        # 仮にchainsが以下のように定義されているとします
        chains = {key: LLMChain(llm=self.llm, prompt=PromptTemplate(input_variables=["situation"], template=self._read_prompt(path))) for key, path in self.SETTINGS_PATHS.items()}
        for key, chain in chains.items():
            tools_for_magic.append(Tool(name=f"{key} AI", func=chain.run, description=f"与えられた人物と状況に適切な{key}の呪文を考えることのできるAIです。"))

        tools_for_magic.append(StructuredTool.from_function(name="organize", func=self.parsing_organize, 
                                                            description=
                                                                    "与えられた状況に適切な呪文になるように、最終的に呪文を整形してくれるツールです。"
                                                                    "具体的には、呪文の後に、写真の状況を日本語で記述したものを、コンマで繋いだ形式の文字列を入力として受け取ります。"
                                                                    "例: 'solo, fitness instructor, female, energetic, from above, doing yoga pose, looking up, smiling, closed eyes, ponytail, brown hair, blue eyes, sports bra or tank top, yoga pants or leggings, sports shoes or barefoot, minimal accessories, yoga bracelet, headband, park, morning, sun, bathing in sunlight, energetic smile ,朝の公園でヨガのポーズをとりながら、太陽の光を浴びてエネルギッシュに笑っている。"
                                                                    )
                                                                    )

        tools_for_magic.extend([
            Tool.from_function(
                func=self._instagram_search,
                name="Instagram Search",
                description="Fetches Instagram posts based on a given tag."
            ),
            Tool.from_function(
                func=SerpAPIWrapper().run,
                name="Search",
                description="Useful for answering questions about current events"
            )
        ])

        # Define the agent's prompt
        prefix = """
        インスタグラムに投稿する画像として、以下の人物と状況に適切なものをDALLE2のような画像生成AIのモデルの一つであるstable diffusionで生成することを考えています。
        与えられた状況を十分に考慮した上で、その人物の写真を正確に表現するための呪文を生成してください。
        呪文とは、stable diffusionに送るプロンプトのことです。写真の適切な呪文を考えてください。
        次のツールにアクセスできます:"""
        suffix = """
        では、以下の情報をもとに、推論を開始してください。
        人物: {person}
        状況: {situation}
        {agent_scratchpad}
        """

        prompt_template = ZeroShotAgent.create_prompt(
            tools=tools_for_magic,
            prefix=prefix,
            suffix=suffix,
            input_variables=["person", "situation", "agent_scratchpad"]
        )

        # Initialize the agent and its executor
        llm_chain = LLMChain(llm=self.llm, prompt=prompt_template)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools_for_magic)
        agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools_for_magic, verbose=True)
        return agent_executor.run({"person": person, "situation": situation, "agent_scratchpad": agent_scratchpad})

    def generate_prompt(self, person, situation):
        agent_scratchpad = self.execute_first_stage(person, situation)
        return self.execute_second_stage(person, situation, agent_scratchpad)

    def stage_one(self, person, situation):
        return self.execute_first_stage(person, situation)

    def stage_two(self, person, situation, agent_scratchpad):
        return self.execute_second_stage(person, situation, agent_scratchpad)
    
if __name__=="__main__":
    # 使用例1
    # generator = ImagePromptGenerator()
    # result = generator.generate_prompt("日本人の女子大学生", "スプラッシュマウンテン")
    # print(result)

    # 使用例2
    generator = ImagePromptGenerator()
    stage_one_result = generator.stage_one("日本人の女子大学生", "スプラッシュマウンテン")
    print(stage_one_result)

    stage_two_result = generator.stage_two("日本人の女子大学生", "スプラッシュマウンテン", stage_one_result)
    print(stage_two_result)
