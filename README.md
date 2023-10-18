# ImagePromptGenerator

This project provides a way to generate image prompts based on given scenarios and situations, particularly designed for platforms like Instagram. The main workflow of the program involves two stages: initially generating a scene based on a character and situation and then refining that scene to produce a final result.

## エージェントベースのプロンプト生成システムの解説

このプログラムは、特定の人物とシチュエーションを基に、Stable diffusionのような画像生成AI向けのプロンプトを生成するためのツールキットを提供します。主な仕組みは、エージェントベースのアプローチを採用し、2つのエージェントが役割を担当しています。

### 1つ目のエージェント: シーンの説明と構築
このエージェントは、与えられた人物や状況をもとに、インスタグラムのようなSNSに投稿する写真のシーンを具体的に想像・構築します。

### 2つ目のエージェント: プロンプトの生成
1つ目のエージェントの結果を基に、Stable diffusionのような画像生成AIに適切なプロンプト（呪文とも呼ばれる）を生成します。

これらのエージェントは、さまざまな「ツール」を活用してタスクを達成します。これらのツールは外部APIや内部関数として実装され、エージェントが自動的にアクセス・利用することで、より賢明な決定を下すことができます。

### 主要なツールの一覧と役割:

- SerpAPI: 現在のイベントや情報に関する質問に答えるためのツール。
- Instagram Search: ApifyClientを使用して、特定のタグに基づくインスタグラムの投稿を取得します。これにより、エージェントは人々がどのような内容を投稿しているかのアイディアを得ることができます。
- Organize Tool: 複数の情報やデータポイントを組み合わせ、適切なプロンプトや情報の組み合わせを生成するツールです。
- Various Setting AI Tools: 人物や状況に適切な情報（服装、背景、姿勢など）を提供するためのAI。それぞれの設定ファイルからプロンプトテンプレートを読み込み、それを基に情報を生成します。
- 外部APIに関しては、ApifyClientが利用されており、特定のInstagramタグに基づいて投稿を検索・取得するために使用されます。これにより、現実の投稿の内容やトレンドに基づいて、エージェントがより現実的な判断を下すことが可能となります。


## Prerequisites

- Python 3.x

## Setup

1. Clone the repository:
```bash
git clone [repository_link_here]
cd [repository_directory_name]
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. name the .env.example file to .env:
```bash
mv .env.example .env
```

## Usage

1. To use the program, simply run the main.py script:
```bash
python main.py
```

2. You can modify the character and situation variables in main.py to generate prompts for different scenarios.

## まとめ:
このプログラムは、2つのエージェントと複数のツールを組み合わせて、特定の人物や状況に基づいた画像生成AI向けのプロンプトを効果的に生成することを目指しています。外部APIや内部関数を駆使して、エージェントが自動的に情報を収集・整理し、最終的なプロンプトを提供することが可能です。