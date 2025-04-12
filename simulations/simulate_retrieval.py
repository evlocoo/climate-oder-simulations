import numpy as np
import matplotlib.pyplot as plt

# Observer classes with gamma and tau_char (from Appendix A / Table 1)
observers = {
    "O1": {"gamma": 0.5, "tau_char": 4.5},
    "O2": {"gamma": 0.05, "tau_char": 36},
    "O3": {"gamma": 0.005, "tau_char": 180}
}

# Simulation settings
T = 400            # total simulation time in hours
dt = 1             # timestep in hours
S_max = 1.0        # max entropy convergence
threshold = 0.7    # detection threshold

times = np.arange(0, T, dt)
S_obs = {k: np.zeros_like(times) for k in observers}
detection_times = {k: None for k in observers}

# Run the simulation
for i, t in enumerate(times):
    for k, params in observers.items():
        gamma = params["gamma"]
        tau_char = params["tau_char"]
        tau = t

        # Retrieval law from Equation 4 with tanh smoothing
        dS = gamma * (S_max - S_obs[k][i-1]) * np.tanh(tau / tau_char) if i > 0 else 0
        S_obs[k][i] = S_obs[k][i-1] + dS * dt if i > 0 else 0

        # Detection time
        if detection_times[k] is None and S_obs[k][i] >= threshold:
            detection_times[k] = t

# Print detection times
for k, t in detection_times.items():
    print(f"{k} detected at hour {t}")

# Plot retrieval curves
plt.figure(figsize=(10, 6))
for k in observers:
    plt.plot(times, S_obs[k], label=f"{k} (γ={observers[k]['gamma']}, τ_char={observers[k]['tau_char']})")

plt.axhline(y=threshold, color='gray', linestyle='--', label="Detection threshold (0.7)")
plt.xlabel("Time (τ, hours)")
plt.ylabel("Entropy Convergence S_obs(τ)")
plt.title("Observer-Specific Entropy Retrieval")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("../figures/simulated_retrieval.png")
plt.show()
