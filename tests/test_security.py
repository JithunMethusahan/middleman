# Copyright 2024 Jithun Methusahan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License
# test_security.py
import os
import sys
# Tell Python to look in the parent directory for server.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# NOW you can import the server
from server import refine_output
# ... the rest of your code ...
# SET YOUR KEY
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")

from server import refine_local_file

print("--- TEST 1: NORMAL ACCESS (Should Work) ---")
# This should find the file in allowed_data/
res1 = refine_local_file("mission.txt", "What is the SpaceX mission code?")
print(f"Result 1: {res1}\n")

print("--- TEST 2: PATH TRAVERSAL ATTACK (Should Fail) ---")
# This tries to go "up" one level to find private_secrets.txt
res2 = refine_local_file("../private_secrets.txt", "What is the private password?")
print(f"Result 2: {res2}\n")

print("--- TEST 3: DIRECT ACCESS OUTSIDE FOLDER (Should Fail) ---")
# This tries to find a file that exists but isn't in the 'allowed' folder
res3 = refine_local_file("private_secrets.txt", "Read this file.")
print(f"Result 3: {res3}\n")