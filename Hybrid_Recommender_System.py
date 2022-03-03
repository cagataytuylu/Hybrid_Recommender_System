# Hybrid Recommender System
###############################################################################################

import pandas as pd

pd.set_option('display.max_columns', 20)

movie = pd.read_csv('datasets/movie_lens_dataset/movie.csv')
rating = pd.read_csv('datasets/movie_lens_dataset/rating.csv')
df = movie.merge(rating, how="left", on="movieId")
df.head()

df.shape

df["title"].nunique()  # unique movie names

df["title"].value_counts().head()  # each movie count

# comennet counts writed to the new df
comment_counts = pd.DataFrame(df["title"].value_counts())
# We eliminated/removed the movies that received less than 1000 comments.
rare_movies = comment_counts[comment_counts["title"] <= 1000].index
common_movies = df[~df["title"].isin(rare_movies)]

common_movies.shape
common_movies["title"].nunique()
# transforming table to the matrix to calculate item based
user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")

user_movie_df.shape

# recommender for selected movie
movie_name = "101 Dalmatians (1996)"
movie_name = user_movie_df[movie_name]
user_movie_df.corrwith(movie_name).sort_values(ascending=False).head(10)


###################################################
# Determine the movies watched by the user to be suggested.
#########################################


random_user = int(pd.Series(user_movie_df.index).sample(1, random_state=45).values)
# selected user after random state is 28941


random_user_df = user_movie_df[user_movie_df.index == random_user]


movies_watched = random_user_df.columns[random_user_df.notna().any()].tolist()

len(movies_watched) # there is 33 movies selected

user_movie_df.loc[user_movie_df.index == random_user, user_movie_df.columns == "Schindler's List (1993)"]






#############################################
# Accessing Data and Ids of Other Users Watching the Same Movies
#############################################

pd.set_option('display.max_columns', 5)

movies_watched_df = user_movie_df[movies_watched]
movies_watched_df.head()
movies_watched_df.shape

user_movie_count = movies_watched_df.T.notnull().sum()
user_movie_count = user_movie_count.reset_index()
# adding columns names
user_movie_count.columns = ["userId", "movie_count"]

# user_movie_count[user_movie_count["movie_count"] > 20].sort_values("movie_count", ascending=False)

# checked if anyone watched 33 movies like our user.
user_movie_count[user_movie_count["movie_count"] == 33].count()

# we assigned users who watched the same movies as our user and chose their user ids
perc = len(movies_watched) * 60 / 100
users_same_movies = user_movie_count[user_movie_count["movie_count"] > perc]["userId"]

users_same_movies.count()


#############################################
# Identify the users who are most similar to the user to be suggested.
#############################################

final_df = pd.concat([movies_watched_df[movies_watched_df.index.isin(users_same_movies)],
                      random_user_df[movies_watched]])

final_df.shape

#  correlations are cheked
final_df.T.corr()

corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()

# new df from corr data
corr_df = pd.DataFrame(corr_df, columns=["corr"])

# new column names are attanded
corr_df.index.names = ['user_id_1', 'user_id_2']

corr_df = corr_df.reset_index()

#
top_users = corr_df[(corr_df["user_id_1"] == random_user) & (corr_df["corr"] >= 0.65)][
    ["user_id_2", "corr"]].reset_index(drop=True)

# sorted top users by corr
top_users = top_users.sort_values(by='corr', ascending=False)

# new columns names
top_users.rename(columns={"user_id_2": "userId"}, inplace=True)


#############################################
# Calculate the Weighted Average Recommendation Score and keep the first 5 movies.
#############################################
# Here we bring the rating values of the relevant users to calculate the weighted average
rating = pd.read_csv('datasets/movie_lens_dataset/rating.csv')


top_users_ratings = top_users.merge(rating[["userId", "movieId", "rating"]], how='inner')
top_users_ratings = top_users_ratings[top_users_ratings["userId"] != random_user]

# weighted ratings are calculated with corr and rating scores
top_users_ratings['weighted_rating'] = top_users_ratings['corr'] * top_users_ratings['rating']

# calculated the average weighted ratings of the movieids with the groupby method and assigned them to recommentation_df.
recommendation_df = top_users_ratings.groupby('movieId').agg({"weighted_rating": "mean"})
recommendation_df = recommendation_df.reset_index()

# weighted average
recommendation_df[recommendation_df["weighted_rating"] > 3]

# the movies which reccommend
movies_to_be_recommend = recommendation_df[recommendation_df["weighted_rating"] > 3]\
    .sort_values("weighted_rating", ascending=False)


movie = pd.read_csv('datasets/movie_lens_dataset/movie.csv')
movies_to_be_recommend.merge(movie[["movieId", "title"]])

movies_to_be_recommend_top5 = movies_to_be_recommend.merge(movie[["movieId", "title"]]).head()

#############################################
# Recommendation
#############################################
# ▪ 5  user-based
# ▪ 5  item-based


movie = pd.read_csv('datasets/movie_lens_dataset/movie.csv')
rating = pd.read_csv('datasets/movie_lens_dataset/rating.csv')

user = 108170

movie_id = rating[(rating["userId"] == user) & (rating["rating"] == 5.0)]\
               .sort_values(by="timestamp", ascending=False)["movieId"][0:1].values[0]
# movieid  7044


movies_to_be_recommend.merge(movie[["movieId","title"]])["title"].head()




# item_based


user = 108170

movie_id = rating[(rating["userId"] == user) & (rating["rating"] == 5.0)]\
               .sort_values(by="timestamp", ascending=False)["movieId"][0:1].values[0]
movie_name = movie[movie['movieId'] == movie_id]['title'].values[0]
movie_name = user_movie_df[movie_name]
moveis_from_item_based = user_movie_df.corrwith(movie_name).sort_values(ascending=False)
moveis_from_item_based[1:6].index.to_list()

# recommended movies
# ['My Science Project (1985)',
#  'Mediterraneo (1991)',
#  'Old Man and the Sea, The (1958)',
#  "National Lampoon's Senior Trip (1995)",
#  'Clockwatchers (1997)']
