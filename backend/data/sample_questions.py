"""
Sample Question Bank – seeded into SQLite on first run.
Covers: Software Engineer, Data Scientist, DevOps Engineer, Product Manager
Categories: technical, hr, behavioral
Levels: junior, mid, senior, all
"""

SAMPLE_QUESTIONS = [
    # ── Software Engineer – Technical ──────────────────────────────────────────
    {
        "job_role": "Software Engineer", "category": "technical",
        "experience": "all", "difficulty": "medium",
        "tags": "python,oop,data-structures",
        "question": "What is the difference between a list and a tuple in Python?",
        "model_answer": (
            "Lists are mutable sequences that can be modified after creation, while tuples are "
            "immutable. Lists use square brackets [] and have slightly more overhead due to "
            "mutability. Tuples use parentheses () and are faster, hashable, and suitable as "
            "dictionary keys or set elements. Use lists for collections that change over time "
            "and tuples for fixed data or as dictionary keys."
        ),
    },
    {
        "job_role": "Software Engineer", "category": "technical",
        "experience": "all", "difficulty": "medium",
        "tags": "algorithms,complexity",
        "question": "Explain Big-O notation and why it matters.",
        "model_answer": (
            "Big-O notation describes the worst-case time or space complexity of an algorithm as "
            "input size grows. Common complexities: O(1) constant, O(log n) logarithmic, O(n) "
            "linear, O(n log n) log-linear, O(n²) quadratic. It matters because it helps "
            "developers choose algorithms that scale well. For example, choosing O(n log n) sort "
            "over O(n²) bubble sort dramatically improves performance on large datasets."
        ),
    },
    {
        "job_role": "Software Engineer", "category": "technical",
        "experience": "mid", "difficulty": "hard",
        "tags": "system-design,databases",
        "question": "How would you design a URL shortening service like bit.ly?",
        "model_answer": (
            "Key components: (1) REST API with POST /shorten → returns short code, GET /:code → "
            "redirects. (2) Hash function (base62 encoding of ID) to generate 6-8 char codes. "
            "(3) SQL/NoSQL DB: mapping table (short_code, original_url, created_at, user_id). "
            "(4) Redis cache for hot links. (5) CDN for redirect performance. "
            "Scale considerations: horizontal sharding by short_code hash, separate read/write "
            "replicas, rate limiting per user. Analytics stored in a separate append-only store."
        ),
    },
    {
        "job_role": "Software Engineer", "category": "technical",
        "experience": "junior", "difficulty": "easy",
        "tags": "oop,design-patterns",
        "question": "What are the four pillars of Object-Oriented Programming?",
        "model_answer": (
            "The four pillars are: (1) Encapsulation – bundling data and methods together, hiding "
            "internal state. (2) Abstraction – exposing only necessary interfaces, hiding complexity. "
            "(3) Inheritance – child classes reuse parent class attributes/methods. "
            "(4) Polymorphism – same interface, different implementations (method overriding/overloading). "
            "Example: A Shape class with area() method; Circle and Rectangle override it differently."
        ),
    },
    {
        "job_role": "Software Engineer", "category": "technical",
        "experience": "senior", "difficulty": "hard",
        "tags": "microservices,architecture",
        "question": "What are the trade-offs between microservices and monolithic architecture?",
        "model_answer": (
            "Monoliths: simpler to develop, test, deploy initially; single codebase; no network overhead. "
            "Best for small teams or early-stage products. Microservices: independent deployment, "
            "technology diversity, fault isolation, horizontal scaling per service. "
            "Trade-offs: microservices introduce distributed system complexity (network latency, "
            "data consistency, service discovery, distributed tracing). Use microservices when you "
            "need to scale specific components independently or have multiple teams."
        ),
    },
    {
        "job_role": "Software Engineer", "category": "technical",
        "experience": "all", "difficulty": "medium",
        "tags": "databases,sql",
        "question": "What is a database index and when should you use it?",
        "model_answer": (
            "An index is a data structure (typically B-tree) that speeds up read queries at the cost "
            "of slower writes and additional storage. Use indexes on columns frequently used in WHERE "
            "clauses, JOIN conditions, or ORDER BY. Avoid over-indexing: each index slows INSERT/UPDATE. "
            "Composite indexes cover multiple columns. Always check query execution plans to confirm "
            "indexes are being used."
        ),
    },
    # ── Software Engineer – HR ─────────────────────────────────────────────────
    {
        "job_role": "Software Engineer", "category": "hr",
        "experience": "all", "difficulty": "easy",
        "tags": "behavioral,intro",
        "question": "Tell me about yourself and your engineering journey.",
        "model_answer": (
            "Structure: Present → Past → Future. Start with current role/skills (30 sec), briefly cover "
            "background and key achievements (45 sec), then connect to why you want this role (30 sec). "
            "Keep it under 2 minutes, technical but accessible, and end with enthusiasm for this opportunity."
        ),
    },
    {
        "job_role": "Software Engineer", "category": "hr",
        "experience": "all", "difficulty": "medium",
        "tags": "behavioral,conflict",
        "question": "Describe a time you disagreed with a technical decision. How did you handle it?",
        "model_answer": (
            "Use STAR method. Situation: briefly set context. Task: your role. Action: describe how you "
            "raised concerns professionally (data, prototypes, docs), listened to others' perspectives, "
            "sought consensus or escalated appropriately. Result: outcome and what you learned. "
            "Key: show you can disagree respectfully and still commit to team decisions."
        ),
    },
    # ── Data Scientist – Technical ─────────────────────────────────────────────
    {
        "job_role": "Data Scientist", "category": "technical",
        "experience": "all", "difficulty": "medium",
        "tags": "ml,statistics",
        "question": "Explain the bias-variance trade-off.",
        "model_answer": (
            "Bias = error from wrong assumptions (underfitting). Variance = error from sensitivity to "
            "training data fluctuations (overfitting). High bias: model too simple (e.g. linear model "
            "for non-linear data). High variance: model memorises training data. "
            "Trade-off: reducing bias often increases variance and vice versa. "
            "Solutions: regularisation (L1/L2), cross-validation, ensemble methods, early stopping."
        ),
    },
    {
        "job_role": "Data Scientist", "category": "technical",
        "experience": "mid", "difficulty": "hard",
        "tags": "deep-learning,nlp",
        "question": "How does the Transformer architecture work?",
        "model_answer": (
            "Transformers use self-attention mechanisms to weigh token relationships in parallel "
            "(vs sequential RNNs). Key components: (1) Multi-head attention – captures different "
            "relationship types simultaneously. (2) Positional encoding – injects sequence order. "
            "(3) Feed-forward layers per position. (4) Residual connections + layer norm for stability. "
            "Encoder-decoder for seq2seq tasks; decoder-only (GPT) for generation; encoder-only (BERT) "
            "for classification. O(n²) complexity per layer, addressed by sparse/linear attention variants."
        ),
    },
    {
        "job_role": "Data Scientist", "category": "technical",
        "experience": "all", "difficulty": "medium",
        "tags": "ml,evaluation",
        "question": "What metrics would you use to evaluate a binary classification model?",
        "model_answer": (
            "Depends on class imbalance and business context. Accuracy: misleading on imbalanced data. "
            "Precision: TP/(TP+FP) – minimise false positives (spam filter). "
            "Recall: TP/(TP+FN) – minimise false negatives (cancer detection). "
            "F1: harmonic mean of precision and recall. AUC-ROC: threshold-independent ranking quality. "
            "For imbalanced data: prefer AUC-PR over AUC-ROC. Always align metric with business cost."
        ),
    },
    # ── DevOps Engineer ────────────────────────────────────────────────────────
    {
        "job_role": "DevOps Engineer", "category": "technical",
        "experience": "all", "difficulty": "medium",
        "tags": "docker,containers",
        "question": "Explain the difference between a Docker image and a Docker container.",
        "model_answer": (
            "Image: immutable, layered blueprint (Dockerfile-built). Like a class in OOP. "
            "Container: running instance of an image – isolated process with its own filesystem, network. "
            "Like an object instance. Multiple containers can run from the same image. "
            "Images are stored in registries (Docker Hub, ECR). Containers are ephemeral by default; "
            "use volumes for persistent data."
        ),
    },
    {
        "job_role": "DevOps Engineer", "category": "technical",
        "experience": "mid", "difficulty": "hard",
        "tags": "kubernetes,orchestration",
        "question": "How does Kubernetes handle service discovery and load balancing?",
        "model_answer": (
            "Kubernetes uses Services (ClusterIP, NodePort, LoadBalancer) as stable endpoints. "
            "kube-proxy maintains iptables/IPVS rules to route traffic to healthy Pods. "
            "CoreDNS provides in-cluster DNS: service-name.namespace.svc.cluster.local. "
            "Ingress controllers (NGINX, Traefik) handle external HTTP routing with TLS termination. "
            "For gRPC/TCP load balancing, use a service mesh like Istio."
        ),
    },
    # ── Product Manager ────────────────────────────────────────────────────────
    {
        "job_role": "Product Manager", "category": "technical",
        "experience": "all", "difficulty": "medium",
        "tags": "product,prioritisation",
        "question": "How do you prioritise features in a product backlog?",
        "model_answer": (
            "Use frameworks: (1) RICE score: Reach × Impact × Confidence / Effort. "
            "(2) MoSCoW: Must-have, Should-have, Could-have, Won't-have. "
            "(3) Kano model: basic needs vs delighters. "
            "Process: gather data (user research, analytics, support tickets, sales input), "
            "align with business goals/OKRs, assess engineering effort, build stakeholder consensus. "
            "Re-prioritise quarterly based on new learning."
        ),
    },
    # ── Universal HR/Behavioral ────────────────────────────────────────────────
    {
        "job_role": "All", "category": "hr",
        "experience": "all", "difficulty": "easy",
        "tags": "behavioral,motivation",
        "question": "Why do you want to work at this company?",
        "model_answer": (
            "Research the company's mission, products, culture, and recent news before the interview. "
            "Structure: (1) Specific thing you admire (product, mission, impact). "
            "(2) How your skills/goals align. (3) What you hope to contribute. "
            "Avoid generic answers. Show you've done your homework."
        ),
    },
    {
        "job_role": "All", "category": "hr",
        "experience": "all", "difficulty": "medium",
        "tags": "behavioral,challenge",
        "question": "Tell me about your greatest professional challenge and how you overcame it.",
        "model_answer": (
            "STAR format: Situation (context/stakes), Task (your responsibility), "
            "Action (specific steps YOU took – use 'I', not 'we'), "
            "Result (measurable outcome + what you learned). "
            "Choose a real challenge that shows problem-solving, resilience, and growth. "
            "Quantify results where possible (e.g. 'reduced latency by 40%')."
        ),
    },
    {
        "job_role": "All", "category": "behavioral",
        "experience": "all", "difficulty": "medium",
        "tags": "teamwork,collaboration",
        "question": "Describe a situation where you had to collaborate with a difficult team member.",
        "model_answer": (
            "Focus on your actions and mindset, not blame. Show: empathy (tried to understand their "
            "perspective), communication (direct, private conversation first), "
            "compromise (found common ground), outcome (project success despite friction). "
            "Key lesson: professional relationships require active maintenance."
        ),
    },
    {
        "job_role": "All", "category": "hr",
        "experience": "senior", "difficulty": "medium",
        "tags": "leadership,growth",
        "question": "How do you mentor junior engineers or team members?",
        "model_answer": (
            "Structured approach: (1) Assess their current level through pair programming or code review. "
            "(2) Set clear learning goals aligned with their career aspirations. "
            "(3) Weekly 1:1s – not status updates, but growth discussions. "
            "(4) Give stretch assignments just outside their comfort zone. "
            "(5) Provide timely, specific, actionable feedback. "
            "Measure success by their growing independence and contributions."
        ),
    },
]