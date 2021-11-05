import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import pulp
import networkx as nx
from pyproj import  Geod

# # 5.毎回読み込むと遅いので、キャッシュ化された関数にする
# @st.cache
# def load_data():
#     # 2.データを読み込む
#     # 全国の地方自治体データ
#     localgov_df = pd.read_csv('localgov.csv', usecols=['pref', 'cid', 'city', 'lat', 'lng'])
#     # 政令指定都市は除く
#     seirei = ('札幌市', '仙台市', 'さいたま市', '千葉市', '横浜市', '川崎市', '相模原市', '新潟市', '静岡市', '浜松市',
#             '名古屋市', '京都市', '大阪市', '堺市', '神戸市', '岡山市', '広島市', '北九州市', '福岡市', '熊本市')
#     localgov_df = localgov_df[~localgov_df.city.isin(seirei)]
#     # 全ての自治体どうしの大圏距離
#     df = localgov_df.loc[:, ['cid', 'lat', 'lng']]
#     df['key'] = 1
#     df = pd.merge(df, df, on='key', how='outer',suffixes=['1', '2']).drop('key', axis=1)
#     geod = Geod(ellps='WGS84')
#     def get_distance(lat1, lng1, lat2, lng2):
#         _, _, dist = geod.inv(lng1, lat1, lng2, lat2)
#         return dist
#     df['distance'] = get_distance(df.lat1.tolist(), df.lng1.tolist(), df.lat2.tolist(), df.lng2.tolist())
#     df.distance = df.distance / 1000
#     distance_df = df.loc[:, ['cid1', 'cid2', 'distance']]
#     del df

#     return localgov_df, distance_df

# # 8.最適化する関数
# @st.cache
# def solve_tsp(localgov_dic, distance_dic):

#     nodes = list(localgov_dic.keys())
#     G = nx.Graph()
#     G.add_nodes_from(nodes)
#     edges = [(i, j) for i in nodes for j in nodes if i < j]

#     # 最適化モデルの定義
#     model = pulp.LpProblem('', sense=pulp.LpMinimize)

#     # 決定変数x。枝(i, j)を使うか否か。
#     x = {(i, j):pulp.LpVariable(f'edge({i}, {j})', cat='Binary') for (i, j) in edges}

#     # 制約条件。各都市を必ず1度通る。
#     for i in nodes:
#         avlbl_edges = [(j, i) for j in nodes if (j, i) in edges] + [(i, j) for j in nodes if (i, j) in edges]
#         model += pulp.lpSum( x[edge] for edge in avlbl_edges ) == 2

#     # 目的関数。総距離。
#     model += pulp.lpSum( distance_dic[i, j]['distance'] * x[i, j] for (i, j) in edges )

#     # この条件で解く
#     model.solve()

#     # 使われる枝
#     used_edges = [(i, j) for (i, j) in edges if x[i, j].value() > 0.5]
#     G.add_edges_from(used_edges)

#     # 部分巡回路除去
#     CC = list(nx.connected_components(G))
#     while len(CC) > 1:
#         for S in CC:
#             model += pulp.lpSum( x[i, j] for (i, j) in edges if i in S and j in S ) <= len(S) - 1
#         model.solve()

#         G.remove_edges_from(used_edges)
#         used_edges = [(i, j) for (i, j) in edges if x[i, j].value() > 0.5]
#         G.add_edges_from(used_edges)
#         CC = list(nx.connected_components(G))

#     return model.objective.value(), x

# # 1.タイトルをつける
# st.title('巡回セールスマン問題アプリ')

# # # 2.データを読み込む
# # # 全国の地方自治体データ
# # localgov_df = pd.read_csv('localgov.csv', usecols=['pref', 'cid', 'city', 'lat', 'lng'])
# # # 政令指定都市は除く
# # seirei = ('札幌市', '仙台市', 'さいたま市', '千葉市', '横浜市', '川崎市', '相模原市', '新潟市', '静岡市', '浜松市',
# #         '名古屋市', '京都市', '大阪市', '堺市', '神戸市', '岡山市', '広島市', '北九州市', '福岡市', '熊本市')
# # localgov_df = localgov_df[~localgov_df.city.isin(seirei)]
# # # 全ての自治体どうしの大圏距離
# # distance_df = pd.read_csv('distance.csv')

# localgov_df, distance_df = load_data()

# # 3.チェックボックスをつける
# show_df = st.checkbox('地方自治体データを表示', value=False)

# # 4.データフレームを表示する
# if show_df:
#     st.markdown('### 地方自治体データ')
#     st.dataframe(localgov_df)

# # 6.セレクトボックスで、都道府県を選べるようにする
# selected_pref = st.selectbox('都道府県を選択', options=localgov_df['pref'].unique())
# st.write('選択された都道府県：', selected_pref)

# # 7.選択された都道府県で情報を絞り、最適化のために辞書にする
# # 絞る
# localgov_df = localgov_df[localgov_df.pref==selected_pref]
# distance_df = distance_df[(distance_df.cid1.isin(localgov_df.cid.unique()) & distance_df.cid2.isin(localgov_df.cid.unique()))]
# # 辞書にする
# localgov_dic = localgov_df.set_index('cid').to_dict(orient='index')
# distance_dic = distance_df.set_index(['cid1', 'cid2']).to_dict(orient='index')

# # 8.最適化する関数を用意し、結果を受け取る
# if st.checkbox('最適化計算開始', value=False):
#     st.write('Now solving...')
#     TourLength, x = solve_tsp(localgov_dic, distance_dic)
#     # 使われる枝
#     edges = [(i, j) for (i, j) in x if x[i, j].value()==1]
#     st.write('Solved!')

#     # 9.結果を地図で表示する
#     if st.checkbox('結果を表示', value=False):
#         st.markdown(f'### {selected_pref}の地方自治体を回る巡回路')

#         # 総距離
#         st.write('総距離:', round(TourLength, 1), 'km')

#         # 地図
#         # 下地を用意する。地図の中心の座標や、最初の拡大レベルを指定する
#         tour_map = folium.Map(location=[localgov_df.lat.mean(), localgov_df.lng.mean()], tiles='cartodbpositron', zoom_start=7)
#         # 使われる枝の部分に線を引く
#         for (city_i, city_j) in edges:
#             # 始点と終点の緯度経度
#             both_ends = [
#                 [localgov_dic[city_i]['lat'], localgov_dic[city_i]['lng']]
#                 , [localgov_dic[city_j]['lat'], localgov_dic[city_j]['lng']]
#             ]
#             # 2点間の線を引く
#             folium.vector_layers.PolyLine(
#                 locations=both_ends
#             ).add_to(tour_map)
#             # 各地方自治体の位置にマーカーを置く
#         for city in localgov_dic:
#             # 1つ1つのマーカー
#             folium.Circle(
#                 location=[localgov_dic[city]['lat'], localgov_dic[city]['lng']]
#                 , popup=localgov_dic[city]['city']
#                 , radius=800
#                 , fill=True
#                 , fill_color='#706A73'
#                 , color='#706A73'
#             ).add_to(tour_map)

#         folium_static(tour_map)       
