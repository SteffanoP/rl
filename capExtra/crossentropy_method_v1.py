################
#
# Adaptação do exemplo 1 do Cap. 4 do livro de M. Lapan.
# 
################
from collections import namedtuple

import gym
import numpy as np

from models_torch import PolicyModelCrossentropy, test_policy
from util_plot import plot_result

EpisodeStep = namedtuple('EpisodeStep', field_names=['state', 'action'])


def run_episodes(env, policy_net, batch_size):
    batch_trajectories = []
    batch_returns = []
    for i in range(0,batch_size):
        sum_rewards = 0.0
        trajectory = []
        obs = env.reset()
        is_done = False
        while not is_done:
            # faz uma amostragem da ação, ou seja, 
            # gera uma ação de acordo com as probabilidades retornadas pela rede
            action = policy_net.sample_action(obs)
            next_obs, reward, is_done, _ = env.step(action)
            sum_rewards += reward
            trajectory.append(EpisodeStep(state=obs, action=action))
            obs = next_obs
        batch_trajectories.append(trajectory)
        batch_returns.append(sum_rewards)
    return batch_trajectories, batch_returns


def run_crossentropy_method1(env, total_episodes, ep_batch_size=10, ep_selected_proportion=0.2, initial_policy=None):
    obs_size = env.observation_space.shape[0]
    n_actions = env.action_space.n

    if initial_policy is None:
        policy_model = PolicyModelCrossentropy(obs_size, [128], n_actions, lr=0.01)
    else:
        policy_model = initial_policy.clone()

    all_returns = []

    episodes = 0
    while episodes < total_episodes:
        # 1. Roda alguns episódios
        trajectories, returns = run_episodes(env, policy_model, ep_batch_size)
        all_returns.extend(returns)
        episodes += ep_batch_size

        # 2. Define o valor de corte do "retorno" para os melhores episódios
        return_limit = np.quantile(returns, 1.0-ep_selected_proportion)
        return_mean = float(np.mean(returns))

        # 3. Extrai os estados e ações dos melhores episódios
        states = []
        actions = []
        ep_selected = 0
        for i in range(len(trajectories)):
            if returns[i] >= return_limit:
                ep_selected += 1
                states.extend(map(lambda step: step.state, trajectories[i])) # extrai apenas o estado da lista de passos e insere na lista de treinamento
                actions.extend(map(lambda step: step.action, trajectories[i]))   # extrai apenas o acao da lista de passos e insere na lista de treinamento
            if ep_selected > round(ep_batch_size * ep_selected_proportion):
                break

        # 4. Treina o modelo para reforcar o mapeamento estado-ação
        p_loss = policy_model.partial_fit(states, actions)
 
        print("- episode %d (selected %d): loss=%.3f, return_mean=%.2f, return_limit=%.2f" % (episodes, ep_selected, p_loss, return_mean, return_limit))
    
    return all_returns, policy_model


if __name__ == "__main__":
    #ENV_NAME, rmax = "CartPole-v1", 500
    ENV_NAME, rmax = "Acrobot-v1", 0
    #ENV_NAME, rmax = "LunarLander-v2", 300
    #ENV_NAME, rmax = "MountainCar-v0", 0  # resultados ruins
    ENV = gym.make(ENV_NAME)

    EPISODES   =  400    # total de episódios
    BATCH_SIZE =   20    # quantidade de episódios executados por época de treinamento
    PROPORTION =  0.1    # percentual dos episódios (do batch) que serão selecionados

    policy = PolicyModelCrossentropy(ENV.observation_space.shape[0], [128, 256], ENV.action_space.n, lr=0.01)
    returns, policy = run_crossentropy_method1(ENV, EPISODES, BATCH_SIZE, PROPORTION, initial_policy=policy)

    print("Últimos resultados: media =", np.mean(returns[-20:]), ", desvio padrao =", np.std(returns[-20:]))

    # Exibe um gráfico episódios x retornos (não descontados)
    plot_result(returns, rmax, window=50)

    # Executa alguns episódios de forma NÃO-determinística e imprime um sumário
    test_policy(ENV, policy, False, 5, render=True)

    # Expandindo aqui a execução de alguns episódios de forma DETERMINÍSTICA, para fins didáticos
    for i in range(5):
        print(f"TEST EPISODE {i+1}")
        obs = ENV.reset()
        done = False
        reward = 0.0
        steps = 0
        while not done:
            ENV.render()
            action = policy.best_action(obs) # faz so a acao de maior probabilidade
            obs, r, done, _ = ENV.step(action)
            reward += r
            steps += 1
        ENV.render()
        print("- steps:", steps)
        print("- return:", reward)

    ENV.close()