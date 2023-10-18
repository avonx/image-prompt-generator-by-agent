import generator

def main():
        # Define the character and situation
    character = "日本人の女子大学生"
    situation = "スプラッシュマウンテン"

    # Instantiate the ImagePromptGenerator class
    prompt_generator = generator.ImagePromptGenerator()

    # Stage One: Generate a scene based on character and situation
    generated_scene = prompt_generator.stage_one(character, situation)
    # 例
    # 日本人の女子大学生がスプラッシュマウンテンでインスタグラムに投稿する写真は、滝を下る丸太ボートやディズニーランドの風景を背景に、自分や友人の楽しそうな表情や興奮した様子を撮影したものと考えられます。服装はディズニーランドに来ていることを強調するために、ディズニーキャラクターのアイテムを身につけていると予想されます。
    
    # Print the result of stage one
    print("Stage One Result:")
    print(generated_scene)
    print("-" * 50)  # print a separator for better visibility
    
    # Stage Two: Further refine the scene
    stage_two_result = prompt_generator.stage_two(character, situation, generated_scene)
    # 例
    # 1 girl, Japanese, (20 years old:1.2), short, skinny, wheat skin, looking at viewer, small eyes, button nose, smile, long hair, black hair, raincoat, shorts, hat, bandeau top, full body from behind, looking ahead, standing, waving, arms up, amusement park, Splash Mountain, nature, mountain, waterfall, lake, green, tree, log boat, blue sky, sunny
    
    # Print the result of stage two
    print("Stage Two Result:")
    print(stage_two_result)

if __name__ == "__main__":
    main()