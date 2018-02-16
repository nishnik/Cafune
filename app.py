from flask import Flask, render_template, session, request, redirect
app = Flask(__name__)

import csv
file=open("1488511748129645_facebook_statuses.csv", "r")
reader = csv.reader(file)
data = []
for line in reader:
    data.append(line)

header = data[0]
data = data[1:]

to_remove = []

# simple check to verify the song is on youtube
for row in data:
    if (not 'youtu' in row[6]):
        to_remove.append(row)

print (len(to_remove), len(data))
# print (to_remove)
# row[3][1:-1]
youtube_data = [a for a in data if a not in to_remove]

# Get video id
def parse_yt_url(url):
    if("youtube.com/watch?v" in url):
        return url.split("?v=")[1][:11]
    elif("youtube.com/attribution_link?" in url):
        return url.split("%3D")[1][:11]
    elif("v=" in url):
        return url.split("v=")[-1][:11]
    elif ("youtu.be" in url):
        return url.split("/")[-1][:11]
    else:
        return "-1"

import operator

songs_dict = {} # 'video id' -> [[user_id, reaction_type]]
songs_name = {}
users_name = {}
unparsed = []
for row in youtube_data:
    parsed = parse_yt_url(row[6])
    if (not parsed == "-1"):
        try:
            songs_name[parsed] = row[4]
            songs_dict[parsed].append([str(row[3][1:-1]), 'POST'])
            users_name[str(row[3][1:-1])] = row[2]
            for user in eval(row[-1]):
                songs_dict[parsed].append([user['id'], user['type']])
                users_name[user['id']] = user['name']
        except Exception as e:
            songs_dict[parsed] = []
            songs_dict[parsed].append([str(row[3][1:-1]), 'POST'])
            users_name[str(row[3][1:-1])] = row[2]
            for user in eval(row[-1]):
                songs_dict[parsed].append([user['id'], user['type']])
                users_name[user['id']] = user['name']
    else:
        unparsed.append(row)

users = set()
for dic in songs_dict:
   for val in songs_dict[dic]:
      users.add(val[0])

users_list = list(users)

songs_list = list(songs_dict.keys())

songs_vec = []

import numpy as np
type_val = {'POST':3, 'LOVE':2, 'ANGRY':-2}
for i in range(len(songs_list)):
    tmp = [0]*len(users_list)
    for user, type_ in songs_dict[songs_list[i]]:
        if (type_ in type_val):
            tmp[users_list.index(user)] = type_val[type_]
        else:
            tmp[users_list.index(user)] = 1
    songs_vec.append(tmp)

def dot(K, L):
   if len(K) != len(L):
      return 0
   return sum(i[0] * i[1] for i in zip(K, L))

# from scipy import spatial
# def dot(K, L):
#    if len(K) != len(L):
#       return 0
#    return 1 - spatial.distance.cosine(K, L)

songs_id = {}
for id_ in songs_name:
    name = songs_name[id_]
    if (name in songs_id):
        songs_id[name].append(id_)
    else:
        songs_id[name] = []
        songs_id[name].append(id_)


users_id = {}
for id_ in users_name:
    name = users_name[id_]
    if (name in users_id):
        users_id[name].append(id_)
    else:
        users_id[name] = []
        users_id[name].append(id_)

import numpy as np
songs_vec = np.array(songs_vec)

def top_N_sim_songs(song_id, N = 5):
    INDEX = songs_list.index(song_id)
    sim_songs = {}
    for i in range(len(songs_vec)):
        tmp = dot(songs_vec[i],songs_vec[INDEX])
        sim_songs[songs_list[i]] = tmp
    returned_list = []
    count = 0
    for w in sorted(sim_songs, key=sim_songs.get, reverse=True):
        returned_list.append([songs_name[w], sim_songs[w]])
        count += 1
        if (count == N+1):
            break
    return returned_list[1:]

def top_N_sim_users(user_id, N = 5):
    INDEX = users_list.index(user_id)
    sim_users = {}
    for i in range(songs_vec.shape[1]):
        tmp = dot(songs_vec[:, i],songs_vec[:, INDEX])
        sim_users[users_list[i]] = tmp
    returned_list = []
    count = 0
    for w in sorted(sim_users, key=sim_users.get, reverse=True):
        returned_list.append([users_name[w], w, sim_users[w]])
        count += 1
        if (count == N+1):
            break
    return returned_list

print ("READY")
@app.route('/')
def homepage():
    return str(top_N_sim_users(users_id['Kumar Srinivas'][0], 5))


@app.route('/user', methods=['POST', 'GET'])
def user():
	user_id = request.form['user_id']
	return str(top_N_sim_users(user_id, 5))
    # return str(top_N_sim_users(users_id['Kumar Srinivas'][0], 5))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

