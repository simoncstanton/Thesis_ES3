class Stag_hunt:
    ''' Stag Hunt gameform:
            Semantic View: CC, CD, DC, DD
            Interpretation: RR, ST, TS, PP  ??
                    COL:
                        C       D
            ROW:    C   4,4     1,3
                    D   3,1     2,2
            
            Ordinal representation:
                "g322": [[4,4],[1,3]], [[3,1],[2,2]],
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
            self.matrix = [[4,4],[1,3]],[[3,1],[2,2]]
        else:   #scalar
            #self.matrix = [[5,5],[0,3]],[[3,0],[1,1]]   # locks, Fang et al 2002    [sh.canon.1]
            #self.matrix = [[8,8],[0,7]],[[7,0],[5,5]]   # does not lock
            #self.matrix = [[10,10],[1,8]],[[8,1],[5,5]]  # does not lock (wikipedia Fig 2)
            #self.matrix = [[8,8],[2,6]],[[6,2],[4,4]]  # locks. double ordinal     
            #self.matrix = [[11,11],[5,9]],[[9,5],[7,7]]  # locks, double plus 3        
            self.matrix = [[5,5],[1,3]],[[3,1],[2,2]]   # locks Powers 2010        [sh.canon.2]
            #self.matrix = [[100,100],[0,75]],[[75,0],[25,25]]   # does nto lock [derived from skyrms 2007 but PP value not given]
            #self.matrix = [[4,4],[0,3]],[[3,0],[3,3]] #   does not lock, note does break PP inequalites skyrms 2008
            #self.matrix = [[5,5],[0,4]],[[4,0],[2,2]]   # does not lock, wikipedia risk dominance page
  
        self.semantic_view = ('C', 'D')
        self.mc = [(0,0)]
        
    def reward(self, actions):
        return self.matrix[actions[0]][actions[1]]
    
    def get_semantic_view(self, sv_index):
        return self.semantic_view[sv_index]
