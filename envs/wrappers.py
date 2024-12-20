import numpy as np
import gymnasium as gym


def convert_to_flattened_index(indices, dimensions):
    if len(indices) != len(dimensions):
        raise ValueError("Number of indices must match the number of dimensions")

    flattened_index = 0
    for i in range(len(indices)):
        if indices[i] < 0 or indices[i] >= dimensions[i]:
            raise ValueError(f"Value out of bounds at index {i}: {indices[i]}")
        flattened_index = flattened_index * dimensions[i] + indices[i]

    return flattened_index


# generalizar para um "space discretizer" que converte um espaço contínuo em um espaço discreto
# criar flag para dizer se é para converter para um único bin ou para um array de bins
class GeneralDiscretizer:
    def __init__(self, env, bins_per_dimension):
        assert isinstance(env.observation_space, gym.spaces.Box)
        assert len(env.observation_space.shape) == 1, "Only 1-D observations are supported"
        assert env.observation_space.shape[0] == len(bins_per_dimension), "Number of bins must match the dimensions of the observation"

        self.bins_per_dim = bins_per_dimension.copy()
        self.intervals_per_dim = []
        self.total_bins = 1
        
        for i, bins in enumerate(bins_per_dimension):    
            # cria o 'linspace' do valor inicial ao final
            full_linspace = np.linspace(env.observation_space.low[i], env.observation_space.high[i], bins+1, endpoint=True)
            
            # adiciona o 'linspace' com o valor inicial e o final removidos, por conta do funcionamento do np.digitize():
            #  - valor anterior ao "novo" inicial -> índice "0"
            #  - valor posterior ao "novo" final -> índice "bins-1"
            self.intervals_per_dim.append( full_linspace[1:-1] )
            
            self.total_bins *= bins

    def to_single_bin(self, state):
        bin_vector = [np.digitize(x=state[i], bins=intervals)
                      for i, intervals in enumerate(self.intervals_per_dim)]
        # print(bin_vector)
        return convert_to_flattened_index(bin_vector, self.bins_per_dim)
        #return self._bin_vector_to_single_bin(bin_vector, len(bin_vector)-1)

    '''def _bin_vector_to_single_bin(self, vector, index):
        if index < 0:
            return 0
        return vector[index] + self.bins_per_dim[index] * self._bin_vector_to_single_bin(vector, index-1)
    '''
    
    def get_total_bins(self):
        return self.total_bins


class ObservationDiscretizerWrapper(gym.ObservationWrapper):
    '''Classe para converter espaços contínuos em espaços discretos.

    Esta classe converte ambientes de observações (estados) contínuos em ambientes de estados
    discretos. Especificamente, ele converte representações dadas na forma de array de valores float
    em um único inteiro $\geq$ não-negativo (>=0).
    
    Precisa passar para o construtor uma lista que informa em quantos "bins" vai ser discretizada 
    cada dimensão (ou seja, cada valor float) do espaço de estados original.
    '''
    
    def __init__(self, env, BINS_PER_DIMENSION):
        super().__init__(env)
        # cria um GeneralDiscretizer para converter um array de valores float em um único inteiro >= 0
        # precisa dizer em quantos "bins" vai ser discretizada cada dimensão
        self.discretizer = GeneralDiscretizer(env, BINS_PER_DIMENSION)
        self.observation_space = gym.spaces.Discrete(self.discretizer.get_total_bins())

    def observation(self, obs):
        return self.discretizer.to_single_bin(obs)


class FromDiscreteTupleToDiscreteObs(gym.ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)
        self.observation_space = gym.spaces.Discrete(self._calculate_discrete_size(env.observation_space))

    def _calculate_discrete_size(self, observation_space):
        size = 1
        assert isinstance(observation_space, gym.spaces.Tuple)
        self.dimensions = []
        for space in observation_space:
            size *= space.n
            self.dimensions.append(space.n)
        return size

    def observation(self, observation):
        return convert_to_flattened_index(observation, self.dimensions)
