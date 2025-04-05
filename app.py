import gradio as gr
from proof_of_concept import election

country_percentage, cosine_similarity_df = election.calculate_cosine_similarity()
ko_wu, lai_hsiao, hou_chao = country_percentage

def update_town(county):
    # 依縣市更新鄉鎮市區下拉選單
    town = cosine_similarity_df[cosine_similarity_df['county'] == county]['town'].unique().tolist()
    return gr.Dropdown(choices=town)

def update_village(town):
    # 依鄉鎮市區更新村鄰里下拉選單
    village = cosine_similarity_df[cosine_similarity_df['town'] == town]['village'].unique().tolist()
    return gr.Dropdown(choices=village)

with gr.Blocks() as demo:
    
    theme='John6666/YntecDark'

    gr.Markdown('# 找出章魚里\n'
                f'全國得票率：柯吳配{ko_wu:.2f}, 賴蕭配{lai_hsiao:.2f}, 侯趙配{hou_chao:.2f}')
    
    with gr.Row():
        with gr.Column():
            gr.Markdown('# 餘弦相似度總表')
            gr.DataFrame(cosine_similarity_df)
        
        with gr.Column():
            
            gr.Markdown(f'# 篩選縣市、鄉鎮市區與村鄰里以查看餘弦相似度')
            county_dropdown = gr.Dropdown(
                choices=cosine_similarity_df['county'].unique().tolist(),
                label='選擇縣市',
                interactive=True
            )

            town_dropdown = gr.Dropdown(
                choices=cosine_similarity_df['town'].unique().tolist(),
                label='選擇鄉鎮市區',
                interactive=True
            )

            village_dropdown = gr.Dropdown(
                choices=cosine_similarity_df['village'].unique().tolist(),
                label='選擇村鄰里',
                interactive=True
            )
            filtered_df = gr.DataFrame(cosine_similarity_df)
    
    county_dropdown.change(
        fn=update_town,
        inputs=county_dropdown,
        outputs=town_dropdown
        )
    
    town_dropdown.change(
        fn=update_village,
        inputs=town_dropdown,
        outputs=village_dropdown
        )
    
    village_dropdown.change(
        fn=election.filter_county_town_village,
        inputs=[county_dropdown, town_dropdown, village_dropdown],
        outputs=filtered_df
        )

demo.launch()

# interface= gr.Interface(
#         fn=filter_county_town_village,
#         inputs=[gr.DataFrame(cosine_similarity_df),'text', 'text', 'text'],
#         outputs='dataframe', title='找出章魚里',
#         description=f'輸入你想篩選的縣市名稱、鄉鎮市區與村鄰里。 柯吳配{ko_wu:.4f}, 賴蕭配{lai_hsiao:.4f}, 侯趙配{hou_chao:.4f}')
# interface.launch()