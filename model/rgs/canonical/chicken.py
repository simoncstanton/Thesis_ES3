class Chicken:
    ''' Chicken gameform:
            Semantic View: CC, CD, DC, DD
            Interpretation: R, ST, TS, P
                    COL:
                        C       D
            ROW:    C   4,4     2,5
                    D   5,2     0,0
            
            Ordinal representation:
                "g122": [[3,3],[2,4]], [[4,2],[1,1]],
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
            self.matrix = [[3,3],[2,4]], [[4,2],[1,1]]
        else:
            #self.matrix = [[6,6],[4,9]],[[9,4],[2,2]]      # locks  square of ordinal, -1 on P,P
            #self.matrix = [[6,6],[4,9]],[[9,4],[1,1]]      # locks sqaure of ordinal
            #self.matrix = [[2,2],[1,3]],[[3,1],[0,0]]      # locks https://cs.stanford.edu/people/eroberts/courses/soco/projects/1998-99/game-theory/chicken.html  also https://www-jstor-org.ezproxy.utas.edu.au/stable/223479?seq=5
            #self.matrix = [[9,9],[4,16]],[[16,4],[0,0]]    # locks cube of ordinal, but P,P set to zero
            #self.matrix = [[6,6],[2,7]], [[7,2],[0,0]]   # does not lock. is a variant used as an example for a correlated equilibrium on wikipedia.
            #self.matrix = [[6,6],[2,7]],[[7,2],[1,1]]   # does not lock. is a variant used as an example for a correlated equilibrium on wikipedia.
            #self.matrix = [[1,1],[7,2]],[[2,7],[6,6]]   # does not lock. is a variant used as an example for a correlated equilibrium on wikipedia.
            #self.matrix = [[-100,-100],[-1,10]],[[10,-1],[0,0]]   # does not lock https://math.libretexts.org/Bookshelves/Applied_Mathematics/Introduction_to_Game_Theory%3A_A_Discovery_Approach_(Nordstrom)/04%3A_Non-Zero-Sum_Games/4.02%3A_Prisoner's_Dilemma_and_Chicken
            #self.matrix = [[-100,-100],[10,-1]],[[-1,10],[0,0]] # does not lock [inverted form of the above]
            self.matrix = [[3,3],[1,4]],[[4,1],[0,0]]   # locks Leibo2017
        self.semantic_view = ('C', 'D')
        self.mc = [(0,0)]
        
    def reward(self, actions):
        return self.matrix[actions[0]][actions[1]]
    
    def get_semantic_view(self, sv_index):
        return self.semantic_view[sv_index]
