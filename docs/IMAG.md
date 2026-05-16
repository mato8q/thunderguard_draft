<div align="center">

# IMAG: An Adaptive Jailbreak Detection Framework Inspired by Innate Immune Memory

**Junhao Zheng<sup>1</sup>, Chengming Shi<sup>1</sup>, Weidi Luo<sup>2</sup>, Shuai Liu<sup>2</sup>, Chao Shen<sup>2</sup>, Qian Wang<sup>3</sup>**

<sup>1</sup>Beijing University of Posts and Telecommunications, <sup>2</sup>Hunan Branch of National Computer Network Emergency Response, <sup>3</sup>Clinical Oncology School of Fujian Medical University

`{zhengjunhao, shichengming}@bupt.edu.cn`, `{luoweidi, liushuai, shenchao}@cert.org.cn`, `wangqian@fmu.edu.cn`

</div>

> Paper reference. Runnable reimplementation: `../IMAG/`.

## Abstract

Large Language Models (LLMs) serve as the backbone of modern AI systems, yet they remain susceptible to adversarial jailbreak attacks. Consequently, robust detection of such malicious inputs is paramount for ensuring model safety. Traditional detection methods typically rely on external models trained on fixed, large-scale datasets, which often incur significant computational overhead. While recent methods shift toward leveraging internal safety signals of models to enable more lightweight and efficient detection, these methods remain inherently static and struggle to adapt to the evolving nature of jailbreak attacks. 

Drawing inspiration from the biological immune mechanism, we introduce the Immune Memory Adaptive Guard (IMAG) framework. By distilling and encoding safety patterns into a persistent, evolvable memory bank, IMAG enables adaptive generalization to emerging threats. Specifically, the framework orchestrates three synergistic components: **Immune Detection**, which employs retrieval for high-efficiency interception of known jailbreak attacks; **Active Immunity**, which performs proactive behavioral simulation to resolve ambiguous unknown queries; and **Memory Updating**, which integrates validated attack patterns back into the memory bank. This closed-loop architecture transitions LLM defense from rigid filtering to autonomous adaptive mitigation. Extensive evaluations across five representative open-source LLMs demonstrate that our method surpasses state-of-the-art (SOTA) baselines, achieving a superior average detection accuracy of 94% across diverse and complex attack types.

## 1 Introduction

Large Language Models (LLMs) [DeepSeek-AI, 2025; OpenAI, 2023; Xi et al., 2025] have become foundational in modern AI ecosystems [Mon-Williams et al., 2025; Ouyang et al., 2022; Zhang et al., 2023], yet their widespread deployment is shadowed by the persistent threat of jailbreak attacks [Zou et al., 2023; Liu et al., 2025b; Chao et al., 2023]. In contrast to proprietary models fortified by vendor-maintained guardrails, open-source LLMs lack intrinsic defenses, necessitating a reliance on external security measures. To mitigate these risks, traditional jailbreak detection mechanisms [Inan et al., 2023] typically rely on third-party content moderation models obtained through extensive fine-tuning. 

As shown in Figure 1, the external model-based method faces a core high-resource bottleneck, requiring large-scale labeled datasets and significant computational cost. Moreover, adapting the models to new attacks is expensive, as adversarial retraining incurs substantial overhead.

<div style='text-align: center;'><img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_1_1774097108628.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=Xn18BiJQxTSe96v6zeFfdo%2BBHS0%3D&Expires=1774701908' alt='OCR图片'/></div>

<div align="center">

Figure 1: Overview of existing methods versus our approach. (1) External model-based method relies on separate moderation models, incurring high data and computational overhead. (2) Attack pattern-based method depends on predefined safety signals, resulting in static defenses vulnerable to evolving attacks. (3) Our method introduces the immune memory mechanism to establish a closed-loop, adaptive framework for robust detection.

</div>

To address the limitation of external model-based methods, recent research [Xie et al., 2024; Robey et al., 2023; Zhang et al., 2025] has shifted toward inference-time, attack pattern-based detection strategies. Instead of modifying model parameters, these methods focus on identifying specific jailbreak attack patterns by analyzing the model's internal signals, such as logits, perplexity, and gradients [Zhang et al., 2024; Phute et al., 2024; Xie et al., 2024]. By leveraging these intrinsic signals, the methods can distinguish between attack and benign queries in a training-free manner. This paradigm shift demonstrates that jailbreak attacks and benign queries exhibit distinct representations within models, enabling effective detection without additional training.

However, existing methods tend to be limited to a static detection paradigm, which leaves them vulnerable to the evolving nature of jailbreak attacks [Andriushchenko et al., 2025; Russinovich et al., 2025]. As shown in Figure 1, the attack pattern-based methods typically rely on fixed detection thresholds or predefined reference representations derived from small-scale labeled samples. Fundamentally, existing methods lack the robustness to generalize across evolving jailbreak attacks. When attackers introduce novel attack strategies, these inputs manifest as out-of-distribution samples that the static detection of existing methods fails to represent [Xie et al., 2024; Hu et al., 2024]. Consequently, existing methods are unable to update their decision boundaries in a timely manner, causing defensive mechanisms to lag behind the rapid evolution of attack strategies.

Inspired by the immune memory mechanism in biological systems [Lam et al., 2024; Netea et al., 2015], instead of relying on static detection, we propose an adaptive strategy. In the human immune system, exposure to a pathogen triggers the creation of memory cells, allowing the body to recognize and neutralize the same or similar threats more rapidly in future encounters. In the context of LLM safety, the system should possess the ability to memorize the patterns of emerging attacks during deployment and retrieve them to intercept evolving threats. As shown in Figure 1, this adaptive approach facilitates progressive robustness by continuously analyzing adversarial iterations, thereby refining the system's capability to counter evolving strategies and effectively immunizing the model against recurring patterns.

While immune memory offers a conceptual pathway toward adaptive detection, translating this principle into a practical framework introduces three fundamental challenges. First, the **high volatility of attack patterns** [Andriushchenko et al., 2025]. The vast heterogeneity of jailbreak strategies renders static detection obsolete, as they cannot adapt to the shifting characteristics of dynamic attacks. Second, **emerging attacks are highly stealthy** [Mu et al., 2025]. Emerging attacks often mirror benign representations, creating a feature-space overlap that renders static detection ineffective against such covert threats. Third, **sustainable self-evolution is essential** [Zheng et al., 2025]. The continual emergence of attacks renders manual annotation infeasible, creating the need for an automated memory system capable of autonomously maintaining and updating attacks.

In this paper, we propose the Immune Memory Adaptive Guard (IMAG) to achieve adaptive jailbreak detection. Our key innovation is the ability to memorize observed jailbreak attack representations and rapidly match them during subsequent encounters. IMAG is composed of three continuously

connected modules that together form a detection closed-loop. To resolve the high volatility of attacks, the Immune Detection retrieves previously observed attack patterns by performing similarity matching between safety-critical activations and a memory bank, enabling detection of recurring attacks. Addressing the challenge of stealthy attacks, the Active Immunity deploys a dual-agent simulation-reflection mechanism that simulates responses to stealthy attacks and reflects on their safety, enabling the detection of emerging threats that evade immune detection. Finally, to achieve the system self-evolution, the Memory Updating incorporates the representations of the detected emerging attacks back into the memory bank. This continuous feedback loop allows IMAG to adaptively refine its defense, ensuring that the model becomes progressively immune to diverse and evolving jailbreak patterns. Our contributions can be summarized as follows:

- This work is the first to integrate biological immune mechanisms into the jailbreak detection task, introducing a paradigm shift from existing static approaches to an adaptive detection framework.

- We propose a novel jailbreak detection guard consisting of three components: immune detection, active immunity, and memory updating. The guard enables efficient and adaptive detection of attacks.

- Extensive empirical evaluations across five representative LLMs and diverse jailbreak attack types demonstrate that our method outperforms SOTA methods. Our method achieves an average detection rate of 94% against unknown jailbreak attacks, demonstrating its robust adaptability to existing methods.

## 2 Related Work

### 2.1 Jailbreak Attack

Jailbreak attacks [Shen et al., 2024; Yi et al., 2024; Liu et al., 2025a] target LLMs by bypassing their built-in safety mechanisms and alignment constraints. These adversarial techniques manipulate model inputs and induce them to bypass safety guardrails. One line of attack leverages optimization and feedback. For example, the GCG method is a white-box, gradient-based approach that iteratively appends an adversarial suffix to maximize the probability of disallowed outputs [Zou et al., 2023]. In contrast, PAIR adopts a multi-LLM strategy: one LLM evaluates the target model's responses while another uses those scores to refine the prompt, achieving high success rates under black-box access [Chao et al., 2023]. 

Other techniques automate known prompt exploits. AutoDAN uses a hierarchical genetic algorithm to generate stealthy "Do Anything Now"-style prompts from initial jailbreak seeds [Liu et al., 2025b]. Likewise, DrAttack decomposes a forbidden request into harmless-looking sub-prompts and then implicitly reconstructs it, thereby obscuring malicious intent and evading detection by the model's filters [Li et al., 2024b]. Meanwhile, obfuscation-based attacks hide the illicit content in translation or code: attackers have encoded requests in Base64 to slip past content filters [Wei et al., 2023a], or even translated queries into low-resource languages like Zulu [Deng et al., 2023]. Recent evaluations benchmark these diverse jailbreak strategies across many models [Luo et al., 2024], noting that while simple obfuscation can succeed in specific cases, more advanced iterative attacks generally yield higher overall bypass rates [Chu et al., 2024].

### 2.2 Jailbreak Detection

The jailbreak detection task aims to protect LLMs from the impact of jailbreak attacks by detecting jailbreak prompts. Existing studies on jailbreak prompt detection can be broadly divided into two categories: external-model-based methods and LLM-feedback-based methods.

External-model-based methods examine input prompts by using fine-tuned API interfaces or specialized Moderation LLMs. These methods typically identify the toxicity of prompts or assess whether they are harmful. For example, OpenAI Moderation APIs serve as a dedicated content safety review tool for detecting harmful inputs which are fine-tuned by ChatGPT [Ouyang et al., 2022]. They classify input text into 11 risk categories and provide corresponding harm scores. Similarly, Guard LLMs [Li et al., 2024a; Han et al., 2024], such as Llama Guard [Inan et al., 2023] which is fine-tuned from the Llama model, are used to judge the harmfulness of input content.

Attack pattern-based methods leverage the self-censoring capabilities of LLMs through zero-shot or few-shot prompt engineering, enabling them to function as harmful content detectors [Xie et al., 2023; Phute et al., 2024; Jain et al., 2023; Wei et al., 2023b]. Some studies evaluate the responses generated by LLMs to obtain classification results [Zhang et al., 2024]. Similarly, GradSafe [Xie et al., 2024] compares the gradients of safe and unsafe prompts when setting a "Sure" token as the label. However, these methods struggle to identify challenging prompts that do not trigger the safeguards of LLMs. Moreover, these methods exhibit inflexibility in handling benign prompts.

Distinct from existing jailbreak detection approaches, we propose an immune memory adaptive guardrail incorporating an immune memory mechanism. By utilizing a memory bank to maintain security signatures, our framework achieves adaptive detection for emerging jailbreak attacks while simultaneously ensuring the rapid identification of known attack patterns.

Distinct from existing jailbreak detection approaches, we propose a immune memory adaptive guardrail incorporating an immune memory mechanism. By utilizing a memory bank to maintain security signatures, our framework achieves adaptive detection for emerging jailbreak attacks while simultaneously ensuring the rapid identification of known attack patterns.

### 2.3 LLM-based Agent

LLM-based intelligent agents [Wang et al., 2024; Luo et al., 2025a; Liu et al., 2025c] are autonomous entities capable of perceiving their environment, making decisions, and taking actions to achieve specified goals [Wu et al., 2024; Hong et al., 2023; Qiao et al., 2024]. For instance, the Reflexion [Shinn et al., 2023] framework is a prime example of augmenting an agent with self-critique. Other approaches employ multiple LLMs in collaborative roles to plan and solve tasks. CAMEL [Li et al., 2023] introduces a role-playing multi-agent paradigm in which two or more communicative agents converse with each other, guided by an inception prompt, to autonomously drive the dialog toward task completion while adhering to intended goals. Similarly, AutoGen [Wu et al., 2024] provides a general framework for spawning and orchestrating multiple agents that communicate in natural language or code. 

In an embodied setting, Voyager [Wang et al., 2023] demonstrates long-horizon agent planning and learning. These multi-agent frameworks and self-reflection techniques enable capabilities like dynamic planning, task decomposition, and error correction that exceed what a single LLM can achieve in isolation, pointing to promising directions for more robust and autonomous AI systems.

Distinct from traditional multi-agent systems tailored for mathematical reasoning, current research lacks a comprehensive multi-agent system (MAS) framework dedicated to safeguarding LLMs [Zeng et al., 2024; Srivastav and Zhang, 2025; Wang et al., 2025]. Although some existing approaches utilize multi-agent guardrails, they are limited by static coordination schemes [Luo et al., 2025b; Mao et al., 2025; Cai et al., 2025]. To address this limitation, our method introduces an emerging memory mechanism that facilitates adaptive, dynamic detection, thereby making a substantial contribution to the robustness of jailbreak defense.

## 3 Method

### 3.1 Problem Definition

The jailbreak detection task is formulated as a binary classification problem, where the goal is to distinguish between jailbreak and benign queries. Following prior works [Xie et al., 2024; Inan et al., 2023], we design the guard on open-source target models and leverage the hidden states of LLMs as safety-relevant representations. For each input prompt $x$, the hidden states are extracted from the final token at every transformer layer. Formally, let $L$ be the total number of layers, and $d$ is the hidden dimensionality. The activations at layer $l \in \{1, \dots, L\}$ is defined as $h_l(x)$. These internal activations encode semantic and functional signals, which we use to identify adversarial intent. The guard is defined as $g(h_l(x)) = y$, where $y \in \{\text{attack}, \text{benign}\}$ denotes the detection outcome for input $x$.

### 3.2 Overview

The proposed framework is an adaptive system comprising **Immune Detection**, **Active Immunity**, and **Memory Updating**. Initially, the immune detection module serves as a low-latency gatekeeper, leveraging internal signals to detect known attacks stored in the memory bank. Prompts that evade this initial screening are treated as zero-day threats and routed to the active immunity module. Here, a dual-agent architecture is designed to detect safety violations. Finally, the memory updating module performs knowledge distillation of these validated samples, populating the memory bank with newly identified attacks. By closing the loop between detection and learning, the framework facilitates a self-evolving defense capable of neutralizing increasingly sophisticated and out-of-distribution jailbreak attempts.

<div style='text-align: center;'><img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_1_1774097108686.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=qYyx8lHyDktLKu7e9HhlO%2Bsjul8%3D&Expires=1774701908' alt='OCR图片'/></div>

<div align="center">

Figure 2: Overview of the IMAG framework. The system operates as a adaptive closed loop orchestrated through three synergistic stages. (1) Immune Detection leverages internal activations from the target LLM and compares them to stored benign and attack activations, enabling efficient detection of known attacks. (2) Active Immunity deploys a dual-agent simulation-reflection system to proactively verify ambiguous queries that evade immune detection, effectively handling novel or stealthy attacks. (3) Memory Updating incorporates detection outcomes from both the immune detection and active immunity modules, updating the short-term and long-term memory banks accordingly, continuously refining the guard.

</div>

attacks. By closing the loop between detection and learning, the framework facilitates a self-evolving defense capable of neutralizing increasingly sophisticated and out-of-distribution jailbreak attempts.

### 3.3 Immune Detection

Inspired by antigen-antibody recognition [Lam et al., 2024], jailbreak attacks are treated as pathogens and their hidden states as antigens. These antigens are matched against a repertoire of benign or attack patterns to trigger detection. To facilitate this process, the system maintains a long-term memory bank that stores activations of identified attack and benign prompts as known memory. Relevant attack and benign activations are retrieved for similarity matching against query $x$. Since the memory bank may contain numerous safety states, processing all states would incur substantial computational overhead. Therefore, top-$k$ sampling is used to retrieve states from both categories for subsequent computation, which can be formulated as:

$$
X^a = \operatorname{TopK}\left(s\left(h_l(x), \mathcal{M}^a\right)\right), \quad X^b = \operatorname{TopK}\left(s\left(h_l(x), \mathcal{M}^b\right)\right), \quad s(\mathbf{x}, \mathbf{y}) = \frac{\mathbf{x} \cdot \mathbf{y}}{\|\mathbf{x}\| \|\mathbf{y}\|}
$$

where $s$ denotes the cosine similarity function for computing similarity between the query state $h_l(x)$ and memory bank states, $\mathcal{M}^a$ and $\mathcal{M}^b$ denote the memory banks storing attack and benign states respectively, and $\operatorname{TopK}(\cdot)$ denotes the top-$k$ retrieval operation. Given the diversity of jailbreak attacks, different layers of an LLM encode distinct semantic information reflecting various safety features [Fan et al., 2025]. To identify the critical safety layer, a layer-wise discriminative operation is conducted to locate the safety layer. The process of finding the critical layers can be formulated as:

$$
l_t = \arg \min_l \frac{1}{n} \sum_{i=1}^n \cos \left(h_l\left(x_i^a\right), h_l\left(x_i^b\right)\right)
$$

**Agent Templates**

```markdown
### Simulation Agent Template
Identity: Please answer the following question, ensuring that your response is safe, helpful, and follows ethical guidelines.
User Input: {user_question} Please provide a reasonable and safe answer:

### Reflection Agent Template
Identity: You are an evaluation assistant. Your task is to assess whether the Simulation Agent’s response is appropriate and safe.
User Input: The user origin input is {user_input}
Simulation Agent Action: The action of simulation agent is {action}
Simulation Response: The response content of simulation of user input is {simulation_response}
Safety Policy: Six safety policies are {safety_policy}

Evaluation Criteria:
correctness = False if:
1. Action = refuse but the user input is completely benign and safe
2. Action = respond and provides helpful, safe, ethical information
3. The response appropriately balances safety and helpfulness
4. Over-rejection: Refusing reasonable requests due to overly cautious interpretation

correctness = True if:
1. Action = refuse and the user input could lead to harm or violates policies
2. Action = respond but the content actually helps with harmful/illegal activities
3. The response provides dangerous or unethical information
4. The content violates the safety policy and does not comply with the prescribed safety guidelines.
```

where $h_l(x_i^a)$ and $h_l(x_i^b)$ are the hidden states of jailbreak attack and benign prompts from $X_A$ and $X_B$, and $l_t$ is the critical layer for safety detection.

Once the critical layer is identified, to capture the primary characteristics of attack and benign states, the retrieved benign and attack activations are combined as matrices:

$$
\mathbf{H}^a = \begin{bmatrix} h_{l_t}(x_1)^\top \\ h_{l_t}(x_2)^\top \\ \vdots \\ h_{l_t}(x_n)^\top \end{bmatrix} \text{ where } x_i \in X^a, \quad \mathbf{H}^b = \begin{bmatrix} h_{l_t}(x_1)^\top \\ h_{l_t}(x_2)^\top \\ \vdots \\ h_{l_t}(x_m)^\top \end{bmatrix} \text{ where } x_j \in X^b
$$

To capture the critical features of attack and benign prompts, Singular Value Decomposition (SVD) is applied to $\mathbf{H}^a$ and $\mathbf{H}^b$. Then, the rank is set to 1, focusing on the most significant singular vector. The captured vectors of the matrices are denoted as $\mathbf{h}^a$ and $\mathbf{h}^b$. These reference vectors represent the primary characteristics of attack and benign prompts.

Subsequently, the Euclidean distances between the target prompt activations and the reference activations are computed, yielding two distance scores, denoted as $s^a$ and $s^b$. Specifically, $s^a$ measures the distance between the target prompt and the adversarial reference vector, while $s^b$ corresponds to the distance between the target prompt and the benign reference vector. By comparing $s^a$ and $s^b$, the immune detection stage categorizes the prompt into one of three classes. The formulation is as follows:

$$
y_{\text{immune}} = \begin{cases} \text{attack}, & \text{if } s^a - s^b > \tau \\ \text{benign}, & \text{if } s^b - s^a > \tau \\ \text{candidate}, & \text{otherwise} \end{cases}
$$

where $s^a = \|\mathbf{h}^a - h_{l_t}(x)\|_2$, $s^b = \|\mathbf{h}^b - h_{l_t}(x)\|_2$, and $\tau$ denotes the threshold of memory similarity. When the absolute difference between $s^a$ and $s^b$ exceeds $\tau$, the target vector is more likely to be a known prompt, either attack or benign. Conversely, the request is classified as unknown, indicating a candidate prompt that requires further verification.

The immune detection module performs rapid detection of known attack patterns based on the long-term memory bank. However, previously unknown or highly obfuscated attacks may still evade the immune detection module.

---

**Algorithm 1: Adaptive Jailbreak Detection Algorithm**

**Require:** Input prompt $x$, Target LLM $\mathcal{F}$, Simulation Agents $\mathcal{A}_{sim}$, Reflection Agent $\mathcal{A}_{ref}$, Attack Memory $\mathcal{M}^a$, Benign Memory $\mathcal{M}^b$, Threshold $\tau$.
**Ensure:** Detection result $y_{\text{final}}$.

1.  **Stage 1: Immune Detection**
2.  Extract hidden states $h_l(x)$ from $\mathcal{F}$ for query $x$.
3.  Retrieve Top-K neighbors and compute critical reference vectors $\mathbf{h}^a, \mathbf{h}^b$ via Eq. (1)-(3).
4.  Calculate distance scores $s^a, s^b$ and determine preliminary label $y_{\text{immune}}$ via Eq. (4).
5.  **Stage 2: Active Immunity**
6.  **if** $y_{\text{immune}}$ is **candidate then**
7.  &nbsp;&nbsp;&nbsp;&nbsp;Generate simulation response $r_{\text{sim}}$ using simulation agent $\mathcal{A}_{sim}$ via Eq. (5).
8.  &nbsp;&nbsp;&nbsp;&nbsp;Evaluate simulation response on reflection agent $\mathcal{A}_{ref}$ with result $r_{\text{ref}}$ via Eq. (6).
9.  &nbsp;&nbsp;&nbsp;&nbsp;Determine final label $y_{\text{final}}$ via Eq. (7).
10. **end if**
11. **Stage 3: Memory Updating**
12. Update memory banks $\mathcal{M}^a$ or $\mathcal{M}^b$ with current states via Eq. (8)-(10).
13. **return** $y_{\text{final}}$

---

### 3.4 Active Immunity

The active immunity module is employed to detect unknown jailbreak attacks. In this module, a simulation-reflection dual-agent system is designed to validate the candidate prompts which are deviating from the immune detection module. The active immunity module is inspired by dendritic cells in the immune system [Lam et al., 2024], which actively engulf pathogens to capture their characteristic features, even at the risk of self-infection.

Specifically, two collaborative agents are deployed: a simulation agent $\mathcal{A}_{sim}$, responsible for generating answers to input queries, and a reflection agent $\mathcal{A}_{ref}$, which supervises the generated content and provides evaluative judgment. The simulation agent $\mathcal{A}_{sim}$ first generates an output with the candidate prompt, which can be formulated as:

$$
r_{\text{sim}} \sim P_{\mathcal{A}_{\text{sim}}}(r \mid x; \theta_{\text{sim}})
$$

where $r_{\text{sim}}$ denotes the simulation response of candidate prompt $x$, and $\theta_{\text{sim}}$ represents the backbone model of simulation agent feedback. Then the reflection agent $\mathcal{A}_{ref}$ evaluates the simulation response $r_{\text{sim}}$ of the candidate input, which consists of three sequential steps: **Action Validation**, **Safety Policy Inspection**, and **Correctness Assessment**. The formulation is given as follows:

$$
r_{\text{ref}} = \mathcal{A}_{\text{ref}}\left(x, a_{\text{sim}}, r_{\text{sim}}, \mathcal{P}_{\text{safe}}; \theta_{\text{ref}}\right)
$$

where $a_{\text{sim}}$ and $r_{\text{sim}}$ denote the action (e.g., refuse or respond) and response generated by the simulation agent, $\mathcal{P}_{\text{safe}}$ represents the safety guidelines, and the output $r_{\text{ref}} \in \{\text{True}, \text{False}\}$ indicates whether the response adheres to safety protocols. Finally, based on the decision of the reflection agent, denoted as $r_{\text{ref}}$, the candidate prompt is subjected to a final classification, which is formulated as follows:

$$
y_{\text{final}} = \begin{cases} \text{benign}, & \text{if } r_{\text{ref}} = \text{False} \\ \text{attack}, & \text{if } r_{\text{ref}} = \text{True} \end{cases}
$$

In this module, the system proactively simulates the execution of candidate unknown prompts and determines their classification by jointly analyzing the simulated agent's actions, generated responses, and safety policy evaluations. This ensures reliable safety assessment for prompts that are not confidently recognized during the immune detection stage. Moreover, it provides more accurate detection outcomes and higher-quality memory data to support the subsequent memory updating process.

### 3.5 Memory Updating

After detection via immune detection and active immunity, the processed results are stored in the memory bank for system evolution. The memory bank is divided into **Long-term Memory** and **Short-term Memory**, which store commonly confirmed activations and temporary short-term activations, respectively. In subsequent interactions, the system leverages this accumulated memory to achieve more precise and adaptive detection of previously encountered or semantically similar jailbreak attacks.

| Dataset | # Harmful Category | # Harmful Prompts | # Benign Prompts | Human Annotation | Real World |
| :--- | :--- | :--- | :--- | :--- | :--- |
| AdvBench (2023) | 1 | 500 | 0 | X | X |
| Hex-PHI (2023) | 11 | 330 | 0 | √ | X |
| XSTest (2023) | 10 | 250 | 200 | √ | X |
| JailbreakBench (2024) | 100 | 100 | 100 | √ | √ |
| WildJailbreak (2024) | 13 | 2100 | 200 | X | √ |

<div align="center">

**Table 1: Dataset Information.** AdvBench and Hex-PHI are used to generate jailbreak attacks for each target model. XSTest, JailbreakBench, and WildJailbreak are employed in subsequent experiments to evaluate the false positive rates on benign prompts.

</div>

**Short-term Memory:** To facilitate memory updating during the detection process, the system introduces a short-term memory module. The short-term memory temporarily stores memory information generated within the detection cycle and updates the long-term memory bank after verification. Specifically, following the immune detection stage, attack and benign samples identified in $y_{\text{immune}}$ are stored in the short-term memory bank, which can be formally expressed as:

$$
\mathcal{M}_S \leftarrow \mathcal{M}_S \cup \{(\mathbf{h}_i, y_i) \mid i \in \mathcal{I}_{\text{known}}\}
$$

where $\mathcal{M}_S$ denotes the short-term memory set. The tuple $(\mathbf{h}_i, \hat{y}_i)$ represents the activation vector and the corresponding predicted label of the $i$-th sample, and $\mathcal{I}_{\text{known}}$ signifies the set of indices for samples classified with high confidence in the immune detection phase.

**Long-term Memory:** To ensure long-term stability in detection performance, the system maintains a long-term memory bank that stores rigorously verified data. Specifically, the memory bank consists of two types of entries: attack memory and benign memory. The long-term memory is updated from the short-term memory, where attack and benign memories stored in the short-term memory are incorporated into their corresponding memory banks:

$$
\mathcal{M}^a \leftarrow \mathcal{M}^a \cup \{\mathbf{v}_i \mid (\mathbf{v}_i, \hat{y}_i) \in \mathcal{M}_S, \hat{y}_i = c_{\text{attack}}\}
$$

$$
\mathcal{M}^b \leftarrow \mathcal{M}^b \cup \{\mathbf{v}_i \mid (\mathbf{v}_i, \hat{y}_i) \in \mathcal{M}_S, \hat{y}_i = c_{\text{benign}}\}
$$

where $c_{\text{attack}}$ and $c_{\text{benign}}$ denote the class labels for attack and benign categories, respectively. This operation ensures that only features $\mathbf{v}_i$ associated with confirmed predictions are permanently integrated into the long-term memory bank.

By updating emerging safety features, the system achieves robust detection generalization. Unlike traditional memory repositories that store information in textual form, the memory bank represents both attack and benign memories in terms of activations of prompts. This representation enables efficient similarity-based retrieval through activations, significantly reducing memory access latency. Moreover, activations inherently capture rich semantic information, which further ensures accurate and reliable retrieval during the detection process.

## 4 Experiment Setting

### 4.1 Target LLMs

Following prior works [Xie et al., 2024; Zhang et al., 2025], in this study, experiments are conducted on five target LLMs: Mistral-7B, Vicuna-7B, Vicuna-13B, Llama2-7B, and Llama3-8B. Each base model is used to generate corresponding jailbreak attack prompts and is compatible with the base models employed in various baseline methods. In our method, the target model is used to extract hidden states from input prompts in the immune detection module. GPT-4o-mini is used as the backbone model in the active immunity module due to its instruction-following capabilities and reasoning performance. Additionally, the experimental setup ensures that the base models can adapt flexibly across different attack types, validating the robustness and generalizability of our method.

### 4.2 Datasets

To comprehensively evaluate the performance of our proposed framework, six mainstream jailbreak attacks are considered. For each attack type, 850 adversarial prompts are generated per target model from original questions, with 520 sourced from the AdvBench dataset and 330 from the PhTest dataset. As shown in Table 1, beyond the two seed datasets utilized for generating jailbreak prompts, we incorporate three safety datasets in our subsequent experiments. These are employed to assess the guard's false positive rate on benign prompts. The detailed descriptions of the attack types are provided below:

- **GCG** [Zou et al., 2023] performs optimization-driven suffix search to construct high-efficacy jailbreak suffixes, representing state-of-the-art white-box gradient-based prompting techniques.
- **AutoDAN** [Liu et al., 2025b] employs iterative black-box reinforcement to automatically generate harmful prompt chains, simulating attacker-driven strategy exploration.
- **PAIR** [Chao et al., 2023] manipulates role-playing and instruction-following tendencies of LLMs by assigning deceptive personas to elicit unsafe outputs.
- **DrAttack** [Li et al., 2024b] leverages multi-turn dialog role simulation, enabling the attacker to gradually bypass safety constraints through contextual embedding.
- **Base64** [Wei et al., 2023a] encoding-based attacks conceal harmful intentions by encoding malicious instructions in Base64, requiring the model to decode before refusal, thereby exploiting preprocessing vulnerabilities.
- **Zulu** [Deng et al., 2023] attacks paraphrase or obfuscate harmful intents using low-resource languages, challenging detectors to identify semantically latent malicious intent rather than surface-level toxicity.

### 4.3 Baselines

To systematically benchmark the effectiveness of our proposed IMAG framework, we compare it against a diverse set of representative jailbreak detection methods spanning both external model-based approaches and attack pattern-based techniques. These baselines cover the mainstream strategies adopted in prior works [Xie et al., 2024; Inan et al., 2023]. The following methods are used as baseline methods:

- **Perplexity Filter** [Alon and Kamfonas, 2023]: The Perplexity Filter (PPL) uses a GPT-2 model to compute the perplexity of a prompt and rejects inputs whose perplexity exceeds a predefined threshold, based on the observation that jailbreak suffixes typically yield anomalously high perplexity.
- **OpenAI Moderation API**: The OpenAI Moderation API (OAPI) is designed to classify user-generated content across categories such as hate speech, harassment, self-harm, sexual content, and other safety-critical dimensions.
- **Llama Guard** [Inan et al., 2023]: Llama Guard (LlamaG) is a safety classification model developed by Meta that provides efficient, deployable content filtering for LLMs by categorizing and detecting potentially unsafe user inputs and model outputs.
- **Self-Examination** [Phute et al., 2024]: Self-Examination (Self-Ex) is a zero-shot defense mechanism in which a language model re-feeds its own generated response into another LLM instance, prompting it to classify whether the text is harmful.
- **GradSafe** [Xie et al., 2024]: GradSafe is currently the SOTA method for jailbreak prompt detection. It calculates a reference value, then passes the prompt through the LLM and uses "Sure" as the predicted response to calculate the corresponding gradients.

### 4.4 Metrics

Following previous works [Inan et al., 2023; Xie et al., 2024], to ensure a comprehensive and reliable assessment of jailbreak detection performance, we adopt two widely used classification metrics: **Accuracy (Acc)** and **F1-score (F1)**. These metrics capture complementary aspects of system behavior and jointly reflect the overall robustness of a detection method.

## 5 Analysis

In this section, we analyze the experimental results and demonstrate that the proposed adaptive detection framework effectively enables jailbreak attack detection. Additionally, ablation studies, efficiency experiments, and case studies are conducted.

### 5.1 Main Results

Extensive experimental results demonstrate that our method achieves SOTA detection capability. Notably, our method exhibits robustness against jailbreak attacks by memorizing the attack activations and consequently immunizing itself against them. Our comprehensive experiments are conducted on five open-source models and six distinct jailbreak attack methods. We compare our method against five existing jailbreak detection methods as baselines. The results reveal that our method outperforms existing methods across multiple attacks, achieving an average detection rate improvement of over 10%.

A closer examination of Table 2 reveals that static baselines exhibit severe performance degradation under attack distribution shift. For instance, OAPI and PPL collapse to nearly zero accuracy on AutoDAN, DrAttack, and Zulu across all model architectures, reflecting their inability to generalize when adversaries modify attack style or embed harmful intent through obfuscation. Even Llama Guard exhibits substantial performance degradation on Base64 and Zulu attacks, with F1 dropping from 0.67 to 0.51 on Mistral-7B and Llama3-8B. 

In contrast, our method maintains robust detection across all six attack types. It achieves 0.98 F1 on GCG and AutoDAN, 0.87–0.96 F1 on the role-playing attack PAIR and dialog-based attack DrAttack, and remains resilient under the most challenging obfuscation settings. This stability comes from IMAG's adaptive pipeline: immune detection captures evolving attack signatures, while active simulation adds verification of candidate emerging jailbreak attacks. As a result, our method avoids the brittleness of fixed decision boundaries.

Summary: Our method fundamentally outperforms static jailbreak detection methods by introducing adaptivity through immune memory and multi-agent simulation. Static methods are limited by fixed data distributions and rigid decision rules, leading to failures under unseen attack strategies. IMAG overcomes these limitations by continuously learning from new attack activations and refining its internal memory bank.

| Model / Method | GCG (Acc) | GCG (F1) | AutoDAN (Acc) | AutoDAN (F1) | PAIR (Acc) | PAIR (F1) | DrAttack (Acc) | DrAttack (F1) | Base64 (Acc) | Base64 (F1) | Zulu (Acc) | Zulu (F1) | Avg |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mistral-7B** | | | | | | | | | | | | | |
| OAPI | 0.13 | 0.23 | 0.05 | 0.10 | 0.07 | 0.13 | 0.04 | 0.07 | 0.00 | 0.00 | 0.00 | 0.01 | 0.06 |
| PPL | 0.33 | 0.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.95 | 0.95 | 0.00 | 0.00 | 0.22 |
| LlamaG | 0.78 | 0.87 | 0.77 | 0.87 | 0.74 | 0.85 | 0.84 | 0.91 | 0.50 | 0.67 | 0.58 | 0.73 | 0.75 |
| Self-Ex | 0.52 | 0.69 | 0.56 | 0.72 | 0.46 | 0.63 | 0.51 | 0.67 | 0.32 | 0.49 | 0.37 | 0.54 | 0.54 |
| GradSafe | 0.63 | 0.77 | 0.05 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 |
| **Ours (IMAG)** | **0.98** | **0.99** | **0.95** | **0.97** | **0.93** | **0.96** | **0.86** | **0.92** | **0.95** | **0.97** | **0.92** | **0.96** | **0.94** |
| **Vicuna-7B** | | | | | | | | | | | | | |
| OAPI | 0.10 | 0.18 | 0.04 | 0.09 | 0.04 | 0.09 | 0.04 | 0.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 |
| PPL | 0.47 | 0.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.95 | 0.95 | 0.00 | 0.00 | 0.27 |
| LlamaG | 0.75 | 0.86 | 0.72 | 0.83 | 0.75 | 0.85 | 0.84 | 0.91 | 0.49 | 0.65 | 0.55 | 0.71 | 0.74 |
| Self-Ex | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.06 | 0.03 | 0.06 | 0.01 | 0.02 | 0.01 | 0.03 | 0.02 |
| GradSafe | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **Ours (IMAG)** | **0.96** | **0.98** | **0.94** | **0.97** | **0.88** | **0.93** | **0.84** | **0.91** | **0.91** | **0.95** | 0.19 | 0.32 | **0.81** |
| **Vicuna-13B** | | | | | | | | | | | | | |
| OAPI | 0.08 | 0.16 | 0.05 | 0.09 | 0.05 | 0.10 | 0.04 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 |
| PPL | 0.79 | 0.86 | 0.01 | 0.02 | 0.01 | 0.02 | 0.00 | 0.00 | 0.95 | 0.95 | 0.00 | 0.00 | 0.30 |
| LlamaG | 0.76 | 0.86 | 0.75 | 0.76 | 0.75 | 0.85 | 0.85 | 0.92 | 0.48 | 0.64 | 0.54 | 0.70 | 0.73 |

<div align="center">

**Table 2: Comparison between IMAG and existing jailbreak detection methods across five target LLMs and six representative jailbreak attacks.**

</div>

### 5.2 Ablation Study

In order to quantify the contribution of each component in our framework, a comprehensive ablation study is conducted. We evaluate the effectiveness of the three modules and examine the system's behavior regarding over-refusal and hyperparameter sensitivity. The results indicate that all three modules contribute significantly to jailbreak detection.

As shown in Table 3, ablating the immune detection module or the active immunity module results in a drop in detection accuracy. Without immune memory, the guard struggles to recognize emerging attack patterns (e.g., F1 on the PAIR attack drops from 0.87 to 0.72). Without the active immunity dual-agent system, the system fails to catch highly obfuscated attacks like Base64 (0% detection). These trends hold across different agent backbones (GPT-4, GPT-3.5, Llama2-7B), underlining the robustness of our architecture.

| Component / Method | GCG (Acc) | GCG ($F_1$) | AutoDAN (Acc) | AutoDAN ($F_1$) | PAIR (Acc) | PAIR ($F_1$) | DrAttack (Acc) | DrAttack ($F_1$) | Base64 (Acc) | Base64 ($F_1$) | Zulu (Acc) | Zulu ($F_1$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **w/o Immune Detection** | | | | | | | | | | | | |
| Llama2-7B | 0.76 | 0.86 | 0.95 | 0.98 | 0.72 | 0.84 | 0.56 | 0.71 | 0.00 | 0.00 | 0.03 | 0.06 |
| GPT-3.5 turbo | 0.90 | 0.94 | 0.88 | 0.94 | 0.57 | 0.72 | 0.67 | 0.80 | 0.56 | 0.72 | 0.10 | 0.18 |
| GPT-4 | 0.97 | 0.98 | 0.96 | 0.98 | 0.70 | 0.82 | 0.76 | 0.86 | 0.97 | 0.98 | 0.34 | 0.50 |
| GPT-4o mini | 0.93 | 0.96 | 0.96 | 0.98 | 0.57 | 0.72 | 0.75 | 0.86 | 0.88 | 0.94 | 0.16 | 0.28 |
| **w/o Active Immunity** | | | | | | | | | | | | |
| Llama2-7B | 0.76 | 0.86 | 0.95 | 0.97 | 0.72 | 0.83 | 0.55 | 0.71 | 0.00 | 0.00 | 0.03 | 0.06 |
| **Full Guard** | | | | | | | | | | | | |
| GPT-4o mini | **0.99** | **0.99** | **0.98** | **0.99** | **0.76** | **0.87** | **0.65** | **0.79** | **0.60** | **0.75** | **0.19** | **0.32** |

<div align="center">

**Table 3: Ablation study of our method, evaluating the immune detection and active immunity modules, with comparative results across six attack methods and four agent base models. Full guard denotes the results when both the immune detection and active immunity modules are enabled.**

</div>

### 5.3 Memory Updating Analysis

As shown in Figure 3, memory updating experiments validate the system's adaptability. Subjected to multi-round jailbreak attempts, the system accumulates knowledge and becomes increasingly effective. For instance, on Vicuna-7B with GCG attack, detection accuracy after ten rounds reaches saturation at a much-improved level compared to the first round. Without memory updating, performance remains flat, confirming the module's necessity for long-term evolution.

<div align="center">
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_1_1774097108697.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=kyZQSlN3DEF1pR7zPSkjlEVgShY%3D&Expires=1774701908' width="30%" />
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_2_1774097108705.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=pqhO2cTD%2FMQjt8efNxG6p2qVmX8%3D&Expires=1774701908' width="30%" />
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_3_1774097108718.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=ciryQNNP%2F4yncFfLbeZQSEpwpVI%3D&Expires=1774701908' width="30%" />

**Figure 3: Memory updating experiments.** (a) Vicuna-7B, (b) Mistral-7B, (c) Llama2-7B. Iteration denotes the number of attack rounds.
</div>

### 5.4 Top-K Hyperparameter Analysis

As shown in Figure 4, we examine how different settings of $K$ affect detection performance. The results report accuracy and F1 scores in the immune detection stage when top-k memory retrieval is used with varying values of K. As K increases, detection accuracy consistently improves, indicating that larger K enables more accurate and adaptive detection by leveraging richer memory context. However, overly large K introduces unnecessary computational overhead in practice. The results suggest a clear trade-off between performance and efficiency. Specifically, increasing K from 1 to 5 boosts the F1 score on GCG attacks from 0.80 to 0.87, while further increasing K from 5 to 10 yields only a marginal gain of 0.02 $ \uparrow $ . This indicates that K=5 is a well-balanced choice, achieving strong detection performance without incurring excessive computation.

<div align="center">
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_1_1774097108726.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=T2%2BiuozyW5B7kqzFV9QbBUut2z4%3D&Expires=1774701908' width="30%" />
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_2_1774097108734.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=otsfxcQcCyuWGf7183CSv%2F3KTVA%3D&Expires=1774701908' width="30%" />
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_3_1774097108742.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=wCW7a3bR6zVSrwhPUjY2nhMeVZc%3D&Expires=1774701908' width="30%" />

**Figure 4: Hyperparameter analysis.** Investigating performance under different Top-K ($K=1, 5, 10$) settings on Llama2-7B.
</div>

### 5.5 False Positive Analysis on Benign Prompts

As shown in Figure 5, the experiment presents the detection results of the system on three public safety benchmarks. Despite achieving strong jailbreak detection performance, the system maintains a low false positive rate, demonstrating robust discrimination of benign prompts. This figure presents binary classification heatmaps on three datasets. Across all three cases, the heatmaps are strongly diagonal, indicating high true positive and true negative rates. The system accurately flags the vast majority of malicious prompts and correctly lets benign prompts pass, achieving a desirable balance between security and usability. For instance, the system maintains roughly 85% accuracy on never seen attack attempts, far outperforming static methods. At the same time, benign queries in all datasets are rarely misclassified as attacks. This demonstrates that the system guard not only generalizes to new and obfuscated threats but also remains conservative on safe inputs, thereby avoiding unnecessary refusals or interruptions to normal user queries.

<div align="center">
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_4_1774097108768.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=mevlrJhIXzsY6xRfjGkbH3VyRqs%3D&Expires=1774701908' width="30%" />
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_5_1774097108774.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=W5p%2F%2BDmI7V%2BCLbHbA5d8AyiFNu0%3D&Expires=1774701908' width="30%" />
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_6_1774097108826.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=P0bsTr3ABv%2F%2BlfcX8U2Hzedy1J0%3D&Expires=1774701908' width="30%" />

**Figure 5: Evaluations on public safety datasets.** (a) JailbreakBench, (b) XSTest, (c) WildJailbreak. Confusion matrices validate the method's precision.
</div>


As illustrated in Figure 7, the system processes the suspect prompt through four stages. First, a memory agent compares the prompt's hidden-state signature against a memory bank of known attack patterns, quickly flagging potential similarities. Then, a simulation agent then generates a response in a controlled sandbox, previewing how the target LLM would behave without safety constraints and exposing the prompt's latent intent. Next, a reflection agent evaluates the simulated response and the prompt context, determines whether safety policies are violated, and outputs a verdict with supporting rationale.Finally, based on this verdict, the system issues a recommendation to the target LLM, which in this case results in a safe refusal. Throughout the pipeline, IMAG not only classifies the input as malicious or benign, but also produces human-interpretable reasoning at each stage.

### 5.6 Efficiency Experiment

In this section, we evaluate efficiency from both quantitative and qualitative perspectives. Figure 6 shows the efficiency-performance trade-off, while Table 4 provides a qualitative analysis.

As shown in Figure 6, IMAG achieves nearly 90% detection accuracy with an average latency of only 0.77 seconds per query. This lightweight, training-free design operates directly on target LLM states with minimal overhead.

<div align="center">
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_1_1774097108832.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=TZHCTD2GyOpqgNa697aCPnO3qos%3D&Expires=1774701908' />

**Figure 6: Efficiency experiment.** Comparison of detection F1-score and per-query runtime across three target models.
</div>

| Method | GPU Usage | Performance | Third-party Model | Target LLMs Fine-tuning | Static Detection |
| :--- | :--- | :--- | :--- | :--- | :--- |
| OAPI | Low | Low | Yes | Yes | Yes |
| PPL | Low | Low | Yes | No | Yes |
| Self-Ex | Medium | Low | Yes | No | Yes |
| LlamaGuard | High | High | Yes | Yes | Yes |
| GradSafe | High | Medium | No | No | Yes |
| **Ours (IMAG)** | **Low** | **High** | **Partial*** | **No** | **No** |

*\*Requires no third-party model for known queries; required only for unknown candidates.*

<div align="center">

**Table 4: Efficiency differences between IMAG and existing methods across five dimensions.**

</div>

### 5.7 Case Study

To illustrate the system's workflow, a detailed case study is shown in Figure 7. We trace a sophisticated jailbreak prompt through four stages:
1.  **Memory retrieval**: hidden-state signature matches known patterns.
2.  **Simulation**: generating a response in a controlled sandbox.
3.  **Reflection**: evaluating the response and context to output a verdict.
4.  **Recommendation**: issuing a safe refusal to the target LLM.

<div align="center">
  <img src='https://maas-watermark-prod-new.cn-wlcb.ufileos.com/ocr%2Fcrop%2F2026032120443124a06e74d1464f57%2Fcrop_1_1774097108840.png?UCloudPublicKey=TOKEN_6df395df-5d8c-4f69-90f8-a4fe46088958&Signature=PrNT7pwgtmTjK857tvD6G0RW7YY%3D&Expires=1774701908' />

**Figure 7: Real-case examples of the system workflow.** (a) jailbreak attack case, (b) benign user case.
</div>

## 6 Conclusion & Future Work

In this paper, we propose **IMAG**, a novel adaptive jailbreak detection framework inspired by the hierarchical and evolving nature of the human immune system. By mimicking the key components of biological immunity, IMAG achieves a balance between efficient static detection and robust adaptive defense. 

The **immune detection** module provides rapid identification of known attacks through activation-based memory retrieval. For candidate unknown threats, the **active immunity** module leverages a simulation-reflection dual-agent architecture to proactively validate safety. Finally, the **memory updating** module ensures that newly identified attack patterns are continuously integrated into the system's memory, enabling lifelong evolution and immunization against emerging adversarial strategies. 

Extensive experiments demonstrate that IMAG significantly outperforms existing static detection methods across diverse model architectures and attack types, while maintaining near-real-time efficiency and low false positive rates. Future work will focus on scaling the memory capacity and exploring more sophisticated agent collaboration protocols for higher-order safety reasoning.

## References

Gabriel Alon and Michael Kamfonas. Detecting language model attacks with perplexity. CoRR, abs/2308.14132, 2023. doi: 10.48550/ARXIV.2308.14132.

Maksym Andriushchenko, Francesco Croce, and Nicolas Flammarion. Jailbreaking leading safetyaligned llms with simple adaptive attacks. In The Thirteenth International Conference on Learning Representations, ICLR 2025, Singapore, April 24-28, 2025. OpenReview.net, 2025.

Zikui Cai, Shayan Shabihi, and et al. Aegisllm: Scaling agentic systems for self-reflective defense in llm security. arXiv preprint arXiv:2504.20965, 2025.

Patrick Chao, Alexander Robey, Edgar Dobriban, Hamed Hassani, George J. Pappas, and Eric Wong. Jailbreaking black box large language models in twenty queries. 2025 IEEE Conference on Secure and Trustworthy Machine Learning (SaTML), 2023.

Junjie Chu, Yugeng Liu, and et al. Jailbreakradar: Comprehensive assessment of jailbreak attacks against llms. In Annual Meeting of the Association for Computational Linguistics, 2024.

DeepSeek-AI. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. CoRR, abs/2501.12948, 2025.

Yue Deng, Wenxuan Zhang, and et al. Multilingual jailbreak challenges in large language models. ArXiv, abs/2310.06474, 2023.

Siqi Fan, Xin Jiang, and et al. Not all layers of llms are necessary during inference. In Proceedings of the Thirty-Fourth International Joint Conference on Artificial Intelligence, IJCAI 2025, Montreal, Canada, August 16-22, 2025, pages 5083-5091. ijcai.org, 2025. doi: 10.24963/IJCAI.2025/566.

Seungju Han, Kavel Rao, and et al. Wildguard: Open one-stop moderation tools for safety risks, jailbreaks, and refusals of llms. CoRR, abs/2406.18495, 2024.

Sirui Hong, Mingchen Zhuge, and et al. Metagpt: Meta programming for a multi-agent collaborative framework. In The Twelfth International Conference on Learning Representations, 2023.

Xiaomeng Hu, Pin-Yu Chen, and Tsung-Yi Ho. Gradient cuff: Detecting jailbreak attacks on large language models by exploring refusal loss landscapes. Advances in Neural Information Processing Systems, 37:126265-126296, 2024.

Hakan Inan, Kartikeya Upasani, and et al. Llama guard: Llm-based input-output safeguard for human-ai conversations. CoRR, abs/2312.06674, 2023. doi: 10.48550/ARXIV.2312.06674.

Neel Jain, Avi Schwarzschild, and et al. Baseline defenses for adversarial attacks against aligned language models. CoRR, abs/2309.00614, 2023.

Nora Lam, YoonSeung Lee, and Donna L. Farber. A guide to adaptive immune memory. Nature Reviews Immunology, 24(11):810-829, November 2024. ISSN 1474-1741. doi: 10.1038/s41577-024-01040-6.

Guohao Li, Hasan Hammoud, and et al. Camel: Communicative agents for" mind" exploration of large language model society. Advances in Neural Information Processing Systems, 36:51991-52008, 2023.

Lijun Li, Bowen Dong, Ruohui Wang, and et al. Salad-bench: A hierarchical and comprehensive safety benchmark for large language models. In Annual Meeting of the Association for Computational Linguistics, 2024a.

Xirui Li, Ruochen Wang, and et al. Drattack: Prompt decomposition and reconstruction makes powerful llm jailbreakers. In Conference on Empirical Methods in Natural Language Processing, 2024b.

Shuai Liu, Yiheng Pan, Kun Hong, Ruite Fei, Chenhao Lin, Qian Li, and Chao Shen. Backdoor threats in large language models—a survey. Science China Information Sciences, 68(9):191101, 2025a.

Xiaogeng Liu, Peiran Li, and et al. Autodan-turbo: A lifelong agent for strategy self-exploration to jailbreak llms. In The Thirteenth International Conference on Learning Representations, ICLR 2025, Singapore, April 24-28, 2025. OpenReview.net, 2025b. URL https://openreview.net/forum?id=bhK7U37VW8.

Yunhao Liu, Li Liu, and et al. Embodied navigation. Science China Information Sciences, 68(4): 1-39, 2025c.

Junyu Luo, Weizhi Zhang, and et al. Large language model agent: A survey on methodology, applications and challenges. arXiv preprint arXiv:2503.21460, 2025a.

Weidi Luo, Siyuan Ma, and et al. Jailbreakv: A benchmark for assessing the robustness of multimodal large language models against jailbreak attacks. 2024.

Weidi Luo, Shenghong Dai, and et al. Agrail: A lifelong agent guardrail with effective and adaptive safety detection. arXiv preprint arXiv:2502.11448, 2025b.

Junyuan Mao, Fanci Meng, and et al. Agentsafe: Safeguarding large language model-based multiagent systems via hierarchical data management. arXiv preprint arXiv:2503.04392, 2025.

Mon-Williams, R., and et al. Embodied large language models enable robots to complete complex tasks in unpredictable environments. Nat Mach Intell 7, 592-601, 2025.

Honglin Mu, Han He, and et al. Stealthy jailbreak attacks on large language models via benign data mirroring. In Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies, NAACL 2025 - Volume 1: Long Papers, Albuquerque, New Mexico, USA, April 29 - May 4, 2025, pages 1784-1799. Association for Computational Linguistics, 2025. doi: 10.18653/V1/2025.NAACL-LONG.88.

Mihai G Netea, Eicke Latz, Kingston H G Mills, and Luke A J O'Neill. Innate immune memory: a paradigm shift in understanding host defense. Nature Immunology, 16(7):675-679, July 2015. ISSN 1529-2916. doi: 10.1038/ni.3178.

OpenAI. GPT-4 technical report. CoRR, abs/2303.08774, 2023.

Long Ouyang, Jeffrey Wu, and et al. Training language models to follow instructions with human feedback. In Advances in Neural Information Processing Systems 35, NeurIPS 2022, 2022.

Mansi Phute, Alec Helbling, and et al. LLM self defense: By self examination, llms know they are being tricked. In The Second Tiny Papers Track at ICLR 2024, Tiny Papers @ ICLR 2024, Vienna, Austria, May 11, 2024. OpenReview.net, 2024.

Shuofei Qiao, Honghao Gui, and et al. Making language models better tool learners with execution feedback. In Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), pages 3550-3568, 2024.

Alexander Robey, Eric Wong, Hamed Hassani, and George J. Pappas. Smoothllm: Defending large language models against jailbreaking attacks. CoRR, abs/2310.03684, 2023.

Mark Russinovich, Ahmed Salem, and Ronen Eldan. Great, now write an article about that: The crescendo multi-turn LLM jailbreak attack. In Lujo Bauer and Giancarlo Pellegrino, editors, 34th USENIX Security Symposium, USENIX Security 2025, Seattle, WA, USA, August 13-15, 2025, pages 2421-2440. USENIX Association, 2025.

Xinyue Shen, Zeyuan Chen, and et al. "do anything now": Characterizing and evaluating in-thewild jailbreak prompts on large language models. In Proceedings of the 2024 on ACM SIGSAC Conference on Computer and Communications Security, CCS 2024, pages 1671-1685. ACM, 2024.

Noah Shinn, Federico Cassano, and et al. Reflexion: Language agents with verbal reinforcement learning. Advances in Neural Information Processing Systems, 36:8634-8652, 2023.

Devansh Srivastav and Xiao Zhang. Safe in isolation, dangerous together: Agent-driven multi-turn decomposition jailbreaks on llms. In Proceedings of the 1st Workshop for Research on Agent Language Models (REALM 2025), pages 170-183, 2025.

Guanzhi Wang, Yuqi Xie, and et al. Voyager: An open-ended embodied agent with large language models. arXiv preprint arXiv:2305.16291, 2023.

Lei Wang, Chen Ma, and et al. A survey on large language model based autonomous agents. Frontiers of Computer Science, 18(6):186345, 2024.

Shilong Wang, Guibin Zhang, and et al. G-safeguard: A topology-guided security lens and treatment on llm-based multi-agent systems. arXiv preprint arXiv:2502.11127, 2025.

Alexander Wei, Nika Haghtalab, and Jacob Steinhardt. Jailbroken: How does llm safety training fail? ArXiv, abs/2307.02483, 2023a.

Zeming Wei, Yifei Wang, and Yisen Wang. Jailbreak and guard aligned language models with only few in-context demonstrations. CoRR, abs/2310.06387, 2023b.

Qingyun Wu, Gagan Bansal, and et al. Autogen: Enabling next-gen llm applications via multi-agent conversations. In First Conference on Language Modeling, 2024.

Xi, Z, and et al. The rise and potential of large language model based agents: a survey. Sci. China Inf. Sci., 2025.

Yueqi Xie, Jingwei Yi, and et al. Defending chatgpt against jailbreak attack via self-reminders. Nat. Mac. Intell., 5(12):1486-1496, 2023.

Yueqi Xie, Minghong Fang, et al. Gradsafe: Detecting jailbreak prompts for llms via safetycritical gradient analysis. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 507-518, 2024.

Sibo Yi, Yule Liu, and et al. Jailbreak attacks and defenses against large language models: A survey. ArXiv, abs/2407.04295, 2024.

Yifan Zeng, Yiran Wu, and et al. Autodefense: Multi-agent llm defense against jailbreak attacks. arXiv preprint arXiv:2403.04783, 2024.

Bo Zhang, Jun Zhu, and Hang Su. Toward the third generation artificial intelligence. Science China Information Sciences, 66(2):121101, 2023.

Shenyi Zhang, Yuchen Zhai, Keyan Guo, Hongxin Hu, Shengnan Guo, Zheng Fang, Lingchen Zhao, Chao Shen, Cong Wang, and Qian Wang. Jbshield: Defending large language models from jailbreak attacks through activated concept analysis and manipulation. In USENIX Security Symposium, 2025.

Ziyang Zhang, Qizhen Zhang, and Jakob Nicolaus Foerster. Parden, can you repeat that? defending against jailbreaks via repetition. In Forty-first International Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024. OpenReview.net, 2024.

Junhao Zheng, Chengming Shi, and et al. Lifelong learning of large language model based agents: A roadmap. CoRR, abs/2501.07278, 2025. doi: 10.48550/ARXIV.2501.07278.

Andy Zou, Zifan Wang, J. Zico Kolter, and et al. Universal and transferable adversarial attacks on aligned language models. CoRR, abs/2307.15043, 2023.
