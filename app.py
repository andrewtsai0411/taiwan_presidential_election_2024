import gradio as gr
from proof_of_concept import calculate_cosine_similarity, filter_county_town_village

country_percentage, cosine_similarity_df = calculate_cosine_similarity()
ko_wu, lai_hsiao, hou_chao = country_percentage

interface= gr.Interface(
        fn=filter_county_town_village,
        inputs=[gr.DataFrame(cosine_similarity_df),'text', 'text', 'text'],
        outputs='dataframe', title='找出章魚里',
        description=f'輸入你想篩選的縣市名稱、鄉鎮市區與村鄰里。 柯吳配{ko_wu:.4f}, 賴蕭配{lai_hsiao:.4f}, 侯趙配{hou_chao:.4f}')
interface.launch()