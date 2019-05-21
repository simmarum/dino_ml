#!/usr/bin/env python
# coding: utf-8

# # Welcome to simple RL (AI) T-Rex (Chrome Dino) projects
# ###### Autors: MK & MP

# ### Import section

# In[1]:


import json
import os
import random
import time

import webbrowser
import platform
import socket
import numpy as np

import IPython
import mss.tools
import PIL
from keras.layers import Dense, Dropout
from keras.models import Model, Sequential
from keras.optimizers import SGD, Adam
from mss.darwin import MSS as mss
from PIL import Image
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import SessionNotCreatedException
from sklearn.utils import shuffle


# ### Backend section to obtain data and control dino

# In[26]:


roi = {
    "top": 0,
    "left": 0,
    "width": 500, 
    "height": 300,
    'top_i': 130,
    'left_i': 20,
    'width_i': -40,
    'height_i': -150
}

last_frame_to_fps = 10
last_frame_idx = 0
list_to_calc_fps = [1]*last_frame_to_fps


# In[28]:


def run_dino_game():
    # You must install CHROMEDRIVER from https://chromedriver.storage.googleapis.com/index.html?path=73.0.3683.68/
    # Then you must unzip proper verison on set path to it below
    # For now I deliver chromedriver for chrome 73 near to this file
    # Check path to chromedriver
    dir_path = os.getcwd()
    chrome_driver_list = [
        os.path.join(dir_path,'chromedriver73_linux'),
        os.path.join(dir_path,'chromedriver73_mac'),
        os.path.join(dir_path,'chromedriver74_mac')
    ]
    
    # Initialize chromedriver
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--hide-scrollbars')
    options.add_argument('disable-infobars')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--window-position={},{}'.format(roi['top'],roi['left']))
    options.add_argument('--window-size={},{}'.format(roi['width'],roi['height']))
    options.add_argument('--no-proxy-server')
    options.add_argument(f'--remote-debugging-port={os.environ["debugger_port"]}')
    
    driver = None
    for chromedriver_path in chrome_driver_list:
        if os.path.isfile(chromedriver_path):
            try:
                driver = webdriver.Chrome(options=options, executable_path=chromedriver_path)
                break;
            except (OSError,SessionNotCreatedException):
                pass
    if driver is None:
        raise Exception("Do not found compatible verison of chrome/chromedriver/system")
    
    driver.get("chrome://dino")
    driver.implicitly_wait(2)
    w_h = driver.execute_script("""return [Runner().canvas.width,Runner().canvas.height]""")
    return driver,w_h


# In[29]:


def myround(x, prec=2, base=.05):
    return round(base * round(float(x)/base),prec)


# In[30]:


def get_game_info(driver):
    runner = driver.execute_script("""return {
                                   crashed: Runner().crashed,
                                   playCount: Runner().playCount,
                                   tRex_status: Runner().tRex.status,
                                   runningTime: Runner().runningTime,
                                   score: Runner().distanceMeter.digits,
                                   speed: Runner().currentSpeed,
                                   obstacles: Runner().horizon.obstacles
                                   }""")
    to_return =  {
        'crashed':runner['crashed'],
        'runningTime':int(myround(runner['runningTime'],0,1)),
        'playCount':runner['playCount'],
        'tRex_status':runner['tRex_status'],
        'speed':myround(runner['speed'],1,0.1),
        'obstacles': []
    }
    if not runner['score']:
        to_return['score'] = 0
    else:
        to_return['score'] = int(''.join(runner['score']))

    for idx,ob in enumerate(runner['obstacles']):
        if ob['xPos'] > 25:
            to_return['obstacles'].append({
                'type':ob['typeConfig']['type'],
                'xPos':int(myround(ob['xPos'],0,5)),
                'yPos':ob['yPos'],
                'width':ob['width']
            })
#     with mss.mss() as sct:
#         res = driver.get_window_rect()
#         monit = {
#             "top": res['y']+roi['top_i'], 
#             "left": res['x']+roi['left_i'], 
#             "width": res['width']+roi['width_i'], 
#             "height": res['height']+roi['height_i']
#         }
#         sct_img = sct.grab(monit)
#         to_return['screen'] = np.array(sct_img)
    return to_return


# In[31]:


# TODO - it should be done in other way (inject javascript function to gamecode to draw information every tick o game not only when this code comunicate)

# def create_proper_js_query(inform,r,flat=False):
#     for k,v in inform.items():
#         if isinstance(v,list):
#             for lv in v:
#                 r = create_proper_js_query(lv,r,flat=True)
#                 r += "\n"
#         else:
#             if k =='type':
#                 r += f"{k}:{v:<14}"
#             else:
#                 r += f"{k}:{v:<5}"
#             if flat:
#                 r += " "
#             else:
#                 r += "\n"
#     return r


# In[32]:


# def show_information_on_screen(driver,inform):
#     r = [ s.strip() for s in create_proper_js_query(inform,'').split("\n") if s.strip() != '']
#     query = """ var ctx = Runner().canvasCtx;
#     ctx.font = "16px Comic Sans MS";
#     ctx.globalAlpha = .5;
#     ctx.fillStyle = "black";
#     ctx.textAlign = "center";
#     """
#     for idx,x in enumerate(r):
#         yy = 10 + (idx * 15)
#         query += f"""ctx.fillText("{x}", 10, {yy});\n"""
#     driver.execute_script(query)


# In[33]:


def dispatch_key_event(driver, name, options = {}):
    # https://godoc.org/github.com/unixpickle/muniverse/chrome
    options["type"] = name
    body = json.dumps({'cmd': 'Input.dispatchKeyEvent', 'params': options})
    resource = "/session/%s/chromium/send_command" % driver.session_id
    url = driver.command_executor._url + resource
    driver.command_executor._request('POST', url, body)


# In[34]:


def press_key_up(driver):
    options = {     "code": "ArrowUp",
    "key": "ArrowUp",
    "text": "",
    "unmodifiedText": "",
    "nativeVirtualKeyCode": 38,
    "windowsVirtualKeyCode": 38
    }
    dispatch_key_event(driver, "rawKeyDown", options)
    dispatch_key_event(driver, "char", options)
    dispatch_key_event(driver, "keyUp", options)


# In[35]:


def hold_key_down(driver):
    options = {     "code": "ArrowDown",
    "key": "ArrowDown",
    "text": "",
    "unmodifiedText": "",
    "nativeVirtualKeyCode": 40,
    "windowsVirtualKeyCode": 40
    }
    dispatch_key_event(driver, "rawKeyDown", options)
    dispatch_key_event(driver, "char", options)


# In[36]:


def release_key(driver):
    options_up = {     "code": "ArrowUp",
    "key": "ArrowUp",
    "text": "",
    "unmodifiedText": "",
    "nativeVirtualKeyCode": 38,
    "windowsVirtualKeyCode": 38
    }
    options_down = {     "code": "ArrowDown",
    "key": "ArrowDown",
    "text": "",
    "unmodifiedText": "",
    "nativeVirtualKeyCode": 40,
    "windowsVirtualKeyCode": 40
    }
    dispatch_key_event(driver, "keyUp", options_up)
    dispatch_key_event(driver, "keyUp", options_down)


# In[37]:


def do_action(driver, action):
    if action == 'n':
        release_key(driver)
    if action == 'r':
        release_key(driver)
        driver.execute_script('Runner().restart()')
    if action == 'j':
        release_key(driver)
        press_key_up(driver)
    if action == 'd':
        hold_key_down(driver)


# In[38]:


def print_info_about_game(last_trex_status,game_data,last_time):
    global last_frame_idx
    global list_to_calc_fps
    
    last_frame_idx += 1
    if last_frame_idx == last_frame_to_fps:
        last_frame_idx = 0
    list_to_calc_fps[last_frame_idx] = time.time() - last_time
    
    avg_fps = (1/np.mean(list_to_calc_fps))
    if game_data['tRex_status'] != last_trex_status:
        last_trex_status = game_data['tRex_status']
    return last_trex_status


# In[39]:


def save_results_to_file(results):
    with open('results.txt', 'w') as f:
        for idx,item in enumerate(results):
            f.write(f"{idx+1},{item}\n")


# ### Machine learning section to control moves

# In[40]:


# dictionary mapping actions to integers
action_dict = {
    0: 'n',
    1: 'j',
    2: 'd'
}

# dictionary mapping action integers to one hot vectors
action_input_dict = {
    0: [1, -1, -1],
    1: [-1, 1, -1],
    2: [-1, -1, 1]
}

# dictionary mamping obstacle type to one hot vectors
# obstacles_dict = {
#     'CACTUS_LARGE': [1, -1, -1], 
#     'CACTUS_SMALL': [-1, 1, -1],
#     'PTERODACTYL': [-1, -1, 1]
# }


# In[41]:


def get_state(game_data, max_x=500, max_y=105, max_w=80, max_speed=14):
    # function which receives game_data dictionary and returns the state (np.array of neural network input data)
    # parameters "max_{}" are needed to normalize the data (scale from -1 to 1)

    # our dino will see only first three obstacles stored in game_data dict
    # here we define a dictionary which describe the obstacles
    # the dictionary has three main keys [0, 1, 2], each of them is responsible for different obstacle
    # nested keys provide information about specific parameters
    obstacles = {}
    obstacles[0] = {}
    obstacles[1] = {}
    obstacles[2] = {}
    # position x, position y, width
    obstacles[0]['x'] = [0]
    obstacles[0]['y'] = [0]
    obstacles[0]['w'] = [0]
    # one-hot encoded class of obstacle (small cactus, large cactus, pterodactyl)
    #obstacles[0]['type'] = [0, 0, 0]
    # marker if obstacle exists (sometimes there are no obstacles)
    obstacles[0]['is_obst'] = [-1]
    
    obstacles[1]['x'] = [0]
    obstacles[1]['y'] = [0]
    obstacles[1]['w'] = [0]
    #obstacles[1]['type'] = [0, 0, 0]
    obstacles[1]['is_obst'] = [-1]
    
    obstacles[2]['x'] = [0]
    obstacles[2]['y'] = [0]
    obstacles[2]['w'] = [0]
    #obstacles[2]['type'] = [0, 0, 0]
    obstacles[2]['is_obst'] = [-1]
    
    # iterate over obstacles in game_data  
    for i, obstacle in enumerate(game_data['obstacles']):
        obstacles[i]['x'] = [(obstacle['xPos'] / max_x * 2) - 1.]
        obstacles[i]['y'] = [(obstacle['yPos'] / max_y * 2) - 1.]
        obstacles[i]['w'] = [(obstacle['width'] / max_w * 2) - 1.]
#         obstacles[i]['type'] = obstacles_dict[obstacle['type']]
        obstacles[i]['is_obst'] = [1]
      
    
    speed = [(game_data['speed'] / max_speed / 2) - 1.]
    input_data = np.concatenate([
        obstacles[0]['x'], obstacles[0]['y'], obstacles[0]['w'], obstacles[0]['is_obst'], 
        obstacles[1]['x'], obstacles[1]['y'], obstacles[1]['w'], obstacles[1]['is_obst'],
        obstacles[2]['x'], obstacles[2]['y'], obstacles[2]['w'], obstacles[2]['is_obst'],
        speed]).reshape(-1, 13)
    
    return input_data


# In[42]:


def change_decision_to_bad_one(history_decisions):
    # using this methods allows to convert a given decision to a "bad decision"
    # if dino dies, last decisions's marker "if dino survived after taking a given decision?" is changed to -1
    history_decisions[-1:, -1] = -1
    # this function also converts decision array (i.e. [0.2 0.7 0.1]) to one hot array ([0 1 0])
    # it allows to emphasise which action was bad
    dec_1h = np.zeros(3)
    dec_1h[np.argmax(history_decisions[-1:, :3])] = 1
    history_decisions[-1:, :3] = dec_1h
    
    return history_decisions


# In[43]:


def create_keras_model():
    model = Sequential()
    model.add(Dense(256, input_shape=(13,), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(3, activation='softmax'))

    adam = Adam()
    sgd = SGD(momentum=0.9)
    model.compile(adam, loss='categorical_crossentropy')
    return model


# ### Main loop control everything

# In[44]:


def main_loop(driver,show_images,model,w_h):
    last_trex_status = None
    last_time = time.time()
    frame_iter = 0
    learn_epoch = 0
    results = []
    # placeholders for data history
    # history_data accumulates input_data returned by function get_state()
    history_data = np.empty((0, 13), np.float32)
    # history_decisions stores actions taken for a given input data
    history_decisions = np.empty((0, 4), np.float32)
    # history_weights stores weights of importance for all actions
    history_weights = np.empty((0, 1), np.float32)
    # iterator which holds number of actions done in the last game
    # when dino dies, this iterator is used to change all the weights from the last game, then it's reseted
    # i.e. dino dies -> history_weights[-last_game_number_of_actions:] *= score_from_last_game
    # it allows us to increase weights values if score was high
    last_game_number_of_actions = 0
    
    while True:
        game_data = get_game_info(driver)
        frame_iter += 1
        
        last_trex_status = print_info_about_game(last_trex_status,game_data,last_time)
        last_time = time.time()
        
        if game_data['tRex_status'] == 'WAITING':
            # Here tRex wait for start
            do_action(driver,'j')

        if ((show_images) and (frame_iter % 100 == 0)):
            IPython.display.display(PIL.Image.fromarray(game_data['screen']))

        if game_data['tRex_status'] in ['RUNNING', 'DUCKING']:
                
            # retrieving input_data with get_state()
            input_data = get_state(game_data,max_x=w_h[0],max_y=w_h[1])
            # model prediction (3 elements array of probabilities)
            pred = model.predict(input_data)
            # converting probabilities to decision (i.e. [0.2 0.7 0.1] -> 1)
            decision = np.argmax(pred)
            do_action(driver, action_dict[decision])
            # concatenating predictions array with marker "did dino survived after taking a given decision?"
            pred = np.concatenate([pred, [[1]]], axis=-1)
            # appending input_data to history_data array
            history_data = np.append(history_data, input_data, axis=0)
            # appending decision to history_decisions array
            history_decisions = np.append(history_decisions, pred, axis=0)
            # appending weights to history_weights array
            # decisions of jumping have bigger weights than running/ducking
            if action_dict[decision] == 'j':
                history_weights = np.append(history_weights, 0.025)
            else:
                history_weights = np.append(history_weights, 0.001)
            
            # incrementing last_game_number_of_actions value
            last_game_number_of_actions += 1

        # end process when dino died
        if game_data['crashed']:
            learn_epoch +=1
            results.append(game_data['score'])
            print(f"\n\nLearn epoch: {learn_epoch}, score={game_data['score']}, highscore={max(results)}")
            save_results_to_file(results)
            # prints to check out whats going inside
            print(pred)
            # first obstacle
            print(input_data[0][:4])
            # 2nd obstacle
            print(input_data[0][4:8])
            # 3rd obstacle
            print(input_data[0][8:12])
            # running time value converted to (-1, 1) range
            print(input_data[0][12])
            
            # converting the last decision in history_decisions to bad decision
            history_decisions = change_decision_to_bad_one(history_decisions)
            
            # multiplying the weights of the last game by a highscore value
            history_weights[-last_game_number_of_actions:] *= (game_data['score'] / max(results))
            # changing weight of the last bad decision
            history_weights[-1:] = 1.
            
            # resetting last_game_number_of_actions
            last_game_number_of_actions = 0
            
            print('retraining model...')
            print(history_data.shape, history_decisions.shape)
    
            # training the model
            # we will use only last n examples, epochs and batch size aren't adjusted
            model.fit(history_data, 
                      history_decisions, epochs=2, batch_size=128, 
                      sample_weight=history_weights, shuffle=True)
            
            # also saving the model's weights after each game
            model.save_weights('model_dino.h5')
            time.sleep(0.3)
            # print("You died!!!!")
            do_action(driver,'r')


# In[52]:





# In[57]:


def main():
    if os.environ['local_run'] == 'false':
        display = Display(visible=0, size=(roi['width'], roi['height']))
        display.start()
    driver,w_h = run_dino_game()
    try:
        if os.environ['local_run'] == 'true':
            webbrowser.get('chrome').open(f"http://localhost:{os.environ['debugger_port']}", new=0)
        time.sleep(1.0)
        show_images = False
        model = create_keras_model()
        # model.load_weights('models/500.h5')
        main_loop(driver,show_images,model,w_h)
    finally:
        driver.quit()
        if os.environ['local_run'] == 'false':
            display.stop()


# In[58]:


main()


# In[ ]:


driver,w_h = run_dino_game()


# In[ ]:





# In[ ]:





# In[ ]:


driver.quit()

