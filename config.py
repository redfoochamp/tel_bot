from enum import Enum

token = '1105022847:AAETJsznmLVz31N5jkKKvB57uVWq-EBSGOg'
db_file = 'database.vdb'


class States(Enum):
    S_START = "0"
    S_Prof = "1"
    S_Liquidity = "2"
    S_YearsOff = "3"
