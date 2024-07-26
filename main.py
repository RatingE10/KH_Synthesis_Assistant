import pandas as pd
import requests
import streamlit as st

if 'stage' not in st.session_state:
    st.session_state['stage'] = 0


def button_clicked(stage_num):
    st.session_state['stage'] = stage_num


def synth_list(materials):
    st.html("<h4>This is the list of the necessary materials to craft one of every item in the game.</h4>")
    st.html("<p>This list is static and is meant to be used as a reference. If you want a list relative to your current"
            " materials, try the Material Log.</p>")
    st.dataframe(pd.DataFrame(materials["Shard"], index=['Shards']))
    st.dataframe(pd.DataFrame(materials["Gem"], index=['Gems']))
    st.dataframe(pd.DataFrame(materials["Misc"], index=['Miscellaneous\nMaterials']))

    st.caption("These materials are exclusive to the Final Mix version of the game and come from special Heartless "
               "found in each world.")
    st.dataframe(pd.DataFrame(materials["Stone"], index=['Stones']))


def material_log(needed_materials):
    st.html("<h4>This is the material log. You put in how many you have of each material and we will keep count ("
            "don't refresh or it won't save) and tell you how many you have left.")
    if 'log_state' not in st.session_state:
        st.session_state.log_state = 0

    if st.session_state.log_state is 0:
        st.write(
            "The material log is in Edit Mode. Choose the category of material and the name to input how many of the "
            "material you have. To view all materials of a current category, press this button:")
        log_switch = st.button("Switch to View Mode")
        material_type = st.selectbox("Select a type of material", ["Shard", "Gem", "Misc", "Stone"],
                                     placeholder="Choose a stone")

        match material_type:
            case "Shard":
                st.selectbox("Select a material",
                             ["Blaze", "Bright", "Frost", "Lucid", "Mythril", "Power", "Spirit", "Thunder"],
                             key=material_type)
            case "Gem":
                st.selectbox("Select a material", ["Blaze", "Bright", "Frost", "Lucid", "Power", "Spirit", "Thunder"],
                             key=material_type)
            case "Misc":
                st.selectbox("Select a material",
                             ['Dark Matter', 'Gale', 'Mystery Goo', 'Mythril', 'Orichalcum', 'Serenity Power'],
                             key=material_type)
            case "Stone":
                st.selectbox("Select a material", ["Blazing"], key=material_type)
        with st.form('material_amount'):
            st.number_input(
                "Please input the number of " + st.session_state[material_type] + " " + material_type + "s you have.",
                value=st.session_state.have_materials[material_type][st.session_state[material_type]],
                min_value=0,
                max_value=999,
                key=st.session_state[material_type])
            "Please hit confirm to submit your current change, as it will not be saved otherwise."
            st.form_submit_button("Confirm")
            if st.session_state["FormSubmitter:material_amount-Confirm"]:
                st.session_state.have_materials[material_type][st.session_state[material_type]] = st.session_state[
                    st.session_state[material_type]]
            if st.session_state.have_materials[material_type][st.session_state[material_type]] < \
                    needed_materials[material_type][st.session_state[material_type]]:
                st.error(
                    "You have " + str(
                        st.session_state.have_materials[material_type][st.session_state[material_type]]) + " " + (
                        st.session_state[material_type] if material_type is 'Misc'
                        else (st.session_state[material_type] + " " + material_type)) +
                    ("s. " if st.session_state.have_materials[material_type][
                                  st.session_state[material_type]] != 1 else ". ") + "You need " + str(
                        needed_materials[material_type][st.session_state[material_type]] -
                        st.session_state.have_materials[material_type][st.session_state[material_type]]) + " more.")
            else:
                st.success("Congratulations! You're completely done with this material!")
        if log_switch:
            st.session_state.log_state = 1
            st.rerun()
    if st.session_state.log_state is 1:
        st.write("This is View Mode. Select a category to view how many materials of that type you have.")
        log_switch = st.button("Switch to Edit Mode")

        material_type = st.selectbox("Select a type of material", ["Shard", "Gem", "Misc", "Stone"],
                                     placeholder="Choose a category")
        df = st.dataframe(pd.DataFrame(st.session_state.have_materials[material_type], index=["Your Materials"]))
        materials_left = st.session_state.have_materials[material_type]
        for element in st.session_state.have_materials[material_type]:
            materials_left[element] = material_need[material_type][element] - \
                                      st.session_state.have_materials[material_type][element] if \
                material_need[material_type][element] - st.session_state.have_materials[material_type][
                    element] > 0 else 0
        df.add_rows(pd.DataFrame(materials_left, index=["Materials Left"]))

        if log_switch:
            st.session_state.log_state = 0
            st.rerun()


def recipe_synthesis():
    if 'crafted' not in st.session_state:
        st.session_state.crafted = 0
    st.html("<h4>This is the synthesis page. This has a list of every craftable item, along with their recipe. You "
            "can even see how much you have in comparison how much you need for each item, if you have already "
            "entered the values into the Material Log. Try crafting some yourself!</h4>")
    col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1])
    col2.button("Group 2", key='2')
    col3.button("Group 3", key='3')
    col4.button("Group 4", key='4')
    col5.button("Group 5", key='5')
    col6.button("Group 6", key='6')
    st.html("<p>Note: Crafting recipes past "
            "Group 1 are locked until the requirements are met, but you can press these buttons to bypass that.")

    if st.session_state['2']:
        st.session_state.crafted = 3
    if st.session_state['3']:
        st.session_state.crafted = 9
    if st.session_state['4']:
        st.session_state.crafted = 15
    if st.session_state['5']:
        st.session_state.crafted = 21
    if st.session_state['6']:
        st.session_state.crafted = 30

    reset = st.button("Reset recipes")

    for group in st.session_state.recipes:

        org1, org2, org3 = st.columns([1, 1, 1], vertical_alignment="bottom")

        if group is "2" and st.session_state.crafted < 3:
            st.html(
                "<h3>Sorry, Group 2 isn't unlocked yet. Craft <span style= color:aqua>" + str(
                    3 - st.session_state.crafted) + "</span> more items to be able "
                                                    "to unlock it.")
            break
        elif group is "3" and st.session_state.crafted < 9:
            st.html(
                "<h3>Sorry, Group 3 isn't unlocked yet. Craft <span style= color:aqua>" + str(
                    9 - st.session_state.crafted) + "</span> more items to be able "
                                                    "to unlock it.")
            break
        elif group is 4 and st.session_state.crafted < 15:
            st.html(
                "<h3>Sorry, Group 4 isn't unlocked yet. Craft <span style= color:aqua>" + str(
                    15 - st.session_state.crafted) + "</span> more items to be able "
                                                     "to unlock it.")
            break
        elif group is 5 and st.session_state.crafted < 21:
            st.html(
                "<h3>Sorry, Group 5 isn't unlocked yet. Craft <span style= color:aqua>" + str(
                    21 - st.session_state.crafted) + "</span> more items to be able "
                                                     "to unlock it.")
            break
        elif group is 6 and st.session_state.crafted < 30:
            st.html("<h3>Sorry, Group 7 isn't unlocked yet. You need to craft one of each item to unlock the "
                    "final 3 items.")
            break
        else:
            with org1:
                st.html("<h2>Group " + str(group) + ":</h2>")
            i = 1
        for element in st.session_state.recipes[group]:
            if i is 1:
                with org1:
                    st.session_state.crafted += create_dropdown(element, group)
                i += 1
            elif i is 2:
                with org2:
                    st.session_state.crafted += create_dropdown(element, group)
                i += 1
            elif i is 3:
                with org3:
                    st.session_state.crafted += create_dropdown(element, group)
                i += 1
            if i > 3:
                i = 1
    if reset:
        for group in st.session_state.recipes:
            for element in st.session_state.recipes[group]:
                st.session_state.recipes[group][element]['crafted'] = False
        st.session_state.crafted = 0
        st.rerun()


def create_dropdown(element, group):
    st.write(element)
    crafted = st.session_state.recipes[group][element]['crafted']
    with st.popover(":white_check_mark:" if crafted else " :x:"):
        if crafted:
            st.write("You've already crafted this item.")
            return 1
        else:
            st.html("<h3>To craft the " + element + ", you need:</h3>")
            for key in st.session_state.recipes[group][element]:
                category = 0
                name = 0
                if len(key.split(" ")) is 2:
                    if key.split(" ")[1] is 'Misc':
                        st.write(key.split(" ")[0] + ": " + str(
                            st.session_state.have_materials[key.split(" ")[1]][key.split(" ")[0]]) + "/" + str(
                            st.session_state.recipes[group][element][key]))

                    else:
                        st.write(key + ": " + str(
                            st.session_state.have_materials[key.split(" ")[1]][key.split(" ")[0]]) + "/" + str(
                            st.session_state.recipes[group][element][key]))

                if len(key.split(" ")) is 3:
                    st.write(key.split(" ")[0] + " " + key.split(" ")[1] + ": " + str(
                        st.session_state.have_materials[key.split(" ")[2]][
                            key.split(" ")[0] + " " + key.split(" ")[1]]) + "/" + str(
                        st.session_state.recipes[group][element][key]))
            st.html("<h4>Would you like to craft this item?</h4>")

            to_Craft = st.button("Confirm", key='to_Craft' + element)
            if to_Craft:
                for key in st.session_state.recipes[group][element]:
                    if len(key.split(" ")) is 2:
                        category = key.split(" ")[1]
                        name = key.split(" ")[0]

                    elif len(key.split(" ")) is 3:
                        category = key.split(" ")[2]
                        name = key.split(" ")[0] + " " + key.split(" ")[1]
                    if st.session_state.have_materials[category][name] < st.session_state.recipes[group][element][key]:
                        st.error("Oh no! You're missing " + str(
                            st.session_state.have_materials[category][name] - st.session_state.recipes[group][element][
                                key] * -1) + " " + ((name + " " + category) if category is not 'Misc' else name) + (
                                     "s. " if st.session_state.have_materials[category][name] -
                                              st.session_state.recipes[group][element][key] * -1 != 1 else ". "))
                        return 0
                st.session_state.recipes[group][element]['crafted'] = True
                for key in st.session_state.recipes[group][element]:
                    if len(key.split(" ")) is 2:
                        category = key.split(" ")[1]
                        name = key.split(" ")[0]

                    elif len(key.split(" ")) is 3:
                        category = key.split(" ")[2]
                        name = key.split(" ")[0] + " " + key.split(" ")[1]
                    st.session_state.have_materials[category][name] -= st.session_state.recipes[group][element][key]
                st.rerun()

        return 0


st.title(':red[Kingdom Hearts 1 Final Mix] Synthesis Assistant')

api_data = requests.get('https://cmd3vdwi5tg4ww5eh4uynxmz3y0ncxsh.lambda-url.us-east-2.on.aws/').json()[0]

material_need = api_data['necessary']
# st.write(material_need)
materials_have = api_data['have']
item_recipes = api_data['item']

if 'have_materials' not in st.session_state:
    st.session_state.have_materials = materials_have

if 'recipes' not in st.session_state:
    st.session_state.recipes = item_recipes

st.sidebar.title("KH1FM Synthesis Assistant")
st.sidebar.subheader("Choose one:")
key = st.sidebar.button("Home")
key1 = st.sidebar.button("Synthesis Materials List")
key2 = st.sidebar.button("Synthesis Material Log")
key3 = st.sidebar.button("Recipe Synthesis")

if key:
    button_clicked(0)
elif key1:
    button_clicked(1)
elif key2:
    button_clicked(2)
elif key3:
    button_clicked(3)

match st.session_state['stage']:
    case 0:
        st.html("<h1><b>Hello!</b></h1>")
        st.html("<h3>Welcome to the assistant. Please choose an option on the left to get started.</h3>")
    case 1:
        synth_list(material_need)
    case 2:
        material_log(material_need)
    case 3:
        recipe_synthesis()
