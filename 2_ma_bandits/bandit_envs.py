
import numpy as np


class SimpleMultiArmedBandit :
    '''
    Implementação do chamado "Binary multi-armed bandit" or "Bernoulli multi-armed bandit".
    Cada ação tem uma probabilidade distinta de dar uma recompensa.
    A recompensa é sempre unitária.
    '''

    def __init__(self, actions_reward_probs=[0.1, 0.5], max_steps=4000):
        self.num_arms = len(actions_reward_probs)
        self.arms_prob = tuple(actions_reward_probs)  # probabilidade de cada braço dar uma recompensa
        self.max_steps = max_steps
        self.reset()

    def reset(self):
        self.step_count = 0
    
    def step(self, action):
        self.step_count += 1
        done = (self.step_count == self.max_steps)
        if (np.random.random() <= self.arms_prob[action]):
            return (1.0, done)
        else:
            return (0.0, done)
    
    def get_num_actions(self):
        return self.num_arms

    def get_max_mean_reward(self):
        # método para dar a informação, não deve ser usado em soluções!
        return np.max(self.arms_prob)
    
    def get_max_steps(self):
        return self.max_steps


class GaussianMultiArmedBandit :
    '''
    Implementação do problema que considera uma distribuição normal (gaussiana) das recompensas.
    Cada ação dá recompensans não-nulas com frequência (com casas decimais).
    A recompensa segue um distribuição de probabilidade normal/gaussina, com uma média específica
    (da ação) e com variância 1,0.
    '''
    def __init__(self, actions_mean_reward=[0.1, 0.5], max_steps=4000):
        self.num_arms = len(actions_mean_reward)
        self.arms_means = tuple(actions_mean_reward)
        self.arms_variance = 1.0  # assuming the same for every arm/action
        self.max_steps = max_steps
        self.reset()

    def reset(self):
        self.step_count = 0
    
    def step(self, action):
        self.step_count += 1
        done = (self.step_count == self.max_steps)
        chosen_arm_mean = self.arms_means[action]
        r = np.random.randn() / np.sqrt(self.arms_variance) + chosen_arm_mean
        return r, done

    def get_num_actions(self):
        return self.num_arms
        
    def get_max_mean_reward(self):
        return np.max(self.arms_means)
    
    def get_max_steps(self):
        return self.max_steps



if __name__ == '__main__':
    print("Versão simples")
    env1 = SimpleMultiArmedBandit(max_steps=10)
    done = False
    actions = [1, 0] * 5
    while not done:
        a = actions.pop()
        r, done = env1.step(a)
        print(" - ação", a, ", recompensa", r)


    print("Versão gaussiana")
    env2 = GaussianMultiArmedBandit(max_steps=10)
    done = False
    actions = [1, 0] * 5
    while not done:
        a = actions.pop()
        r, done = env2.step(a)
        print(" - ação", a, ", recompensa", r)

