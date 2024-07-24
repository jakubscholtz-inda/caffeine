import streamlit as st

st.set_page_config(
    page_title="Caffe*in*e",
    page_icon=":coffee:",
    # layout="wide",
)

import streamlit_antd_components as sac
import base64
import uuid
from pymongo import MongoClient
import io
import datetime


@st.cache_resource()
def mongo_client():
    client = MongoClient(st.secrets["mongo_login"])
    return client


@st.cache_resource()
def get_beans():
    client = mongo_client()
    return list(client["caffeine"]["beans"].find({}))


if "voted" not in st.session_state:
    token = st.query_params["token"]
    answer = mongo_client().caffeine.users.find_one({"token": token})
    if answer:
        st.session_state.voted = {}
        st.session_state.votes = {}
        st.session_state.id = str(uuid.uuid4())
    else:
        st.error("Please use the correct link to vote.")
        st.stop()

st.session_state["beans"] = get_beans()


st.title(":coffee: Caffe*in*e ")
st.markdown(" - Please gives us your opinion about our coffee!")
st.markdown(" - 5 cups is the best, 1 cup is the worst rating.")
st.write("After you vote, we will see the price estimate per espresso.")


def vote(index_vote):
    if index_vote not in st.session_state.voted:
        st.toast(f"Thanks for voting {st.session_state.beans[index]['name']}!")
        vote_dict = {
            "name": st.session_state["beans"][index_vote]["name"],
            "date": datetime.datetime.now(),
            "id": st.session_state.id,
            "stars": st.session_state[f"star_{index_vote:02d}"],
        }
        mongo_client().caffeine.votes.insert_one(vote_dict)
        st.session_state.voted[index_vote] = True
        st.session_state.votes[index_vote] = st.session_state[f"star_{index_vote:02d}"]


st.divider()
for index, bean_type in enumerate(st.session_state.beans):
    cols = st.columns([1, 2.5, 0.5, 1, 1.5])
    img = io.BytesIO(base64.b64decode(bean_type["image"]))
    cols[0].image(img, width=80)
    cols[1].write("")
    if "one_time_offer" in bean_type and bean_type["one_time_offer"]:
        cols[1].write(f"**{bean_type['name']}** (limited offer)")
    else:
        cols[1].write(f"**{bean_type['name']}**")

    if index in st.session_state.voted:
        cols[3].write("")
        cols[3].write(f"~ {1.3 * bean_type['price_per_kilo'] / 1000 * 8.3:.2f}€")
    with cols[4]:
        if index not in st.session_state.voted:
            st.write("")
            sac.rate(
                label="",
                value=3.0,
                align="start",
                key=f"star_{index:02d}",
                on_change=vote,
                args=(index,),
                symbol=sac.BsIcon("cup-hot", size=None, color=None),
                size="sm",
            )
        else:
            st.write("")
            st.write(f":red[You voted {st.session_state.votes[index]}]")
    st.divider()
