from heapq import heappush, heappop

class search:
    def __init__(self, init_paths, G, ext_fncn, eval_fncn):
        
        self.init_paths = init_paths
        self.G = G
        self.eval_fncn = eval_fncn
        self.extn_fncn = extn_fncn

    def best_first(self, num_evals=1000):
        heap = []
        for elt in self.init_paths:
            val = -1*self.eval_fncn(elt)
            heappush(heap, (val, elt))
            
        i=0
        while(1):
            if(i > nuM_evals):
                break

            val, elt = heappop(heap)
            new_paths = self.extn_fncn(elt)

            for p in new_paths:
                v = -1*self.eval_fncn(p)
                heappush(heap, (v, p))
            i+=1

        return heappop(heap)
            
            
    
            
