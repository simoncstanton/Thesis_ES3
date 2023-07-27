class Coordination_game:
    ''' Coordination gameform:
            Semantic View: CC, CD, DC, DD
            Interpretation: RR, ST, TS, PP  ??
                    COL:
                        C       D
            ROW:    C   4,4     1,3
                    D   3,1     2,2
            
            Ordinal representation:
                "g311": [4,4],[2,3],[3,2],[1,1]
            ---------------------------------------
                            COL:
                            C/0     D/1
            ROW:    C/0     R       S
                    D/1     T       P
                    
                    [[R],[S]], [[T],[P]]
                    
                            COL:
                            C/0     D/1
            ROW:    C/0     0,0     0,1
                    D/1     1,0     1,1

                    [[R{0,0}],[S{0,1}]], [[T{1,0}],[P{1,1}]]                
    '''
    def __init__(self, properties):
        self.properties = properties
        
        if self.properties["preferences"] == "ordinal":
            self.matrix = [[4,4],[2,3]],[[3,2],[1,1]]
        else:   #scalar
            #self.matrix = [[4,4],[2,3]],[[3,2],[1,1]]   # locks, Fang et al 2002
            #self.matrix = [[8,8],[4,6]],[[6,4],[2,2]]   # locks, double of ordinal 
            self.matrix = [[1,1],[0.333,0.667]],[[0.667,0.333],[0,0]]  # ord.norm; locks, with normal norm + 0.1
        self.semantic_view = ('C', 'D')
        self.mc = [(0,0)]
        
    def reward(self, actions):
        return self.matrix[actions[0]][actions[1]]
    
    def get_semantic_view(self, sv_index):
        return self.semantic_view[sv_index]
