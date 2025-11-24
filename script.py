# -*- coding: utf-8 -*-
import scratchconnect
import numpy as np
import os

SAVE_FILE = "save_file.npy"

# ------------ 1. Load save_file -------------------
if os.path.exists(SAVE_FILE):
    data_list = np.load(SAVE_FILE, allow_pickle=True)
else:
    data_list = np.empty((1, 4), dtype=object)
    data_list[:] = "0"

print("Loaded data_list:")
print(data_list)

# ------------ 2. Credentials (GitHub Secrets) -----
with open("S:\sc_py/pass.txt", "r", encoding="utf-8") as f:
    username = f.readline().strip()
    password = f.readline().strip()

if not username or not password:
    raise Exception("SCRATCH_USERNAME or SCRATCH_PASSWORD not set.")

# ------------ 3. Connect to Scratch ---------------
user = scratchconnect.ScratchConnect(username, password)
project_0 = user.connect_project(project_id=1185564217)
project_1 = user.connect_project(project_id=1193299191)

variables_0 = project_0.connect_cloud_variables()
variables_1 = project_1.connect_cloud_variables()

# ============================================================
# ============= 4. PROJECT 0 (1185564217) =====================
# ============================================================

variables_0.get_variable_data(limit=100, offset=0)
data = variables_0.get_cloud_variable_value("content.element", limit=1)
data_str = str(data)

# "['01.1001']" みたいな形式なので整形
raw = data_str[3:-2]
code = data_str[2:-2]

print("Project0 raw:", raw, "code:", code)

if raw != "":
    mode = code[0]    # 1=entry, 2=delete, 3=save

    if mode == "1":
        exists = np.any(data_list[:, 0] == raw)
        if not exists:
            new_row = np.array([[raw, "0", "0", "0"]], dtype=object)
            data_list = np.vstack((data_list, new_row))
            variables_0.set_cloud_variable("content.element", "01." + raw)
        else:
            variables_0.set_cloud_variable("content.element", "02." + raw)

    elif mode == "2":  # delete
        try:
            user_id, slot = raw.split(".")
            slot = int(slot)
            idx = np.where(data_list[:, 0] == user_id)[0][0]
            data_list[idx, slot] = "0"
            variables_0.set_cloud_variable("content.element", "01." + user_id)
        except:
            variables_0.set_cloud_variable("content.element", "04." + raw)

    elif mode == "3":  # save
        try:
            user_id = raw.split('.')[0]
            rest = raw.split('.')[1]
            slot = int(rest[0])
            project_id = rest[1:]

            idx = np.where(data_list[:, 0] == user_id)[0][0]
            data_list[idx, slot] = project_id + "."
            variables_0.set_cloud_variable("content.element", "01." + user_id)
        except:
            variables_0.set_cloud_variable("content.element", "04." + raw)

# ============================================================
# ============= 5. PROJECT 1 (1193299191) =====================
# ============================================================

variables_1.get_variable_data(limit=100, offset=0)
data1 = variables_1.get_cloud_variable_value("content.element", limit=1)

data1_str = str(data1)
raw1 = data1_str[3:-2]
code1 = data1_str[2:-2]

if raw1 != "":
    mode1 = code1[0]

    if mode1 == "1":  # road
        try:
            idx = np.where(data_list[:, 0] == raw1)[0][0]
            row_str = data_list[idx, :].astype(str)

            if np.char.startswith(row_str, "1193299191").any():
                starts = np.where(np.char.startswith(row_str, "1193299191"))[0]
                idx2 = starts[0]
                project_id = data_list[idx, idx2].split(".")[-1]
                variables_1.set_cloud_variable("content.element", "01" + project_id + "." + raw1)
            else:
                variables_1.set_cloud_variable("content.element", "04." + raw1)

        except Exception as e:
            variables_1.set_cloud_variable("content.element", "04." + raw1)

    if mode1 == "2":  # save
        try:
            name = raw1.split(".")[-1]
            project_id = raw1.split(".")[0]

            idx = np.where(data_list[:, 0] == name)[0][0]
            row_str = data_list[idx, :].astype(str)

            if np.char.startswith(row_str, "1193299191").any():
                starts = np.where(np.char.startswith(row_str, "1193299191"))[0]
                idx2 = starts[0]
                data_list[idx, idx2] = "1193299191." + project_id
                variables_1.set_cloud_variable("content.element", "01." + name)
            else:
                variables_1.set_cloud_variable("content.element", "04." + name)

        except Exception as e:
            variables_1.set_cloud_variable("content.element", "04." + raw1)

# ------------ 6. Save updated data_list --------------------
np.save(SAVE_FILE, data_list)

print("Saved updated data_list:")
print(data_list)
