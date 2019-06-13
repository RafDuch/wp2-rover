from testmerge import TestMerge

class MainRoverMerge:
    
    def __init__(self, test_merge):
        self.test_merge = test_merge

    
    def sendInstruction(self, instruction):
        self.test_merge.set_instruction(instruction)


    def getVoltage(self):
        return (10)#appele fonction qui retourne la voltage des roues


#client = Client.Client(main_rover)

#threading.Thread(target=suivi_ligne.start_rover).start()


test_merge = TestMerge()
main_rover_merge = MainRoverMerge(test_merge)

test_merge.start_rover_connection()

#client.start_connection()