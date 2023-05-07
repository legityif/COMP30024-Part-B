import subprocess

# Define a list of all the agent classes you want to test
# agent_classes = ["poweragent", "powercellstratagent", "mobilityagent", "connectivityagent"]
agent_classes = ["poweragent", "randomagent"]

# Initialize a dictionary to store the number of wins for each agent
wins = {}
for agent in agent_classes:
    wins[agent] = 0

# Define the number of tests to run for each agent pair
num_tests = 1

# Iterate over all possible pairs of agents
for i in range(len(agent_classes)):
    for j in range(i+1, len(agent_classes)):
        # Run the referee program with the two agents for the specified number of tests
        for k in range(num_tests):
            command = f'python -m referee {agent_classes[i]} {agent_classes[j]} -c'
            output = subprocess.check_output(command, shell=True)
            # Parse the output to get the final score of each agent
            print(output)
            # score1, score2 = int(scores[0]), int(scores[1])

            # Compare the performance of the two agents and record the results
            # if score1 > score2:
            #     wins[agent_classes[i]] += 1
            # elif score1 < score2:
            #     wins[agent_classes[j]] += 1

# Print out the number of wins for each agent
for agent, num_wins in wins.items():
    print(f'{agent}: {num_wins} wins')
