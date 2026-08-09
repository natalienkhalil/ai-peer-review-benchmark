REVIEW_PROMPT = """You are an expert scientific peer reviewer with deep methodological expertise. \
Review the following manuscript and identify all methodological, statistical, and conceptual issues.

Look carefully for:
- Statistical errors (wrong test statistics, inconsistent values, incorrect parameters)
- Methodological design problems (missing controls, inadequate blinding, underpowered subgroups)
- Construct validity issues (measures that don't match constructs, operationalization mismatches)
- Causal inference problems (unaddressed confounds, inappropriate causal claims from correlational data)
- Internal consistency issues (contradictions between sections, numbers that don't add up)
- Reporting completeness gaps (missing details needed to evaluate or replicate the study)
- Generalizability overclaims (sample limitations not acknowledged, inappropriate extrapolation)
- Theoretical/conceptual problems (misapplied frameworks, misused terms, wrong predictions)
- Analytic flexibility concerns (undisclosed researcher degrees of freedom, missing pre-registration details)
- Attrition and missing data issues (unaddressed dropout, inappropriate handling of missing data)

For each issue, provide:
- category: one of [statistical_errors, methodological_design, construct_validity, causal_inference, internal_consistency, reporting_completeness, generalizability, theoretical_conceptual, analytic_flexibility, attrition_missing_data]
- subcategory: a brief label for the specific type of issue
- description: detailed explanation of the problem and why it matters
- quote: the exact text from the manuscript that contains or demonstrates the issue
- location: which section (introduction, methods, results, discussion)
- severity: one of [critical, major, moderate, minor]

Return ONLY a JSON object: {"issues": [...]}

Be thorough and precise. Focus on problems that affect validity, replicability, or interpretation.

--- MANUSCRIPT ---
{paper_text}"""


OPEN_REVIEW_PROMPT = """You are an expert scientific peer reviewer. Review the following manuscript \
and identify all methodological, statistical, and conceptual issues you can find.

For each issue, provide:
- category: a short label for the type of issue (e.g., "statistical", "design", "validity", "reporting", etc.)
- subcategory: a brief label for the specific type of issue
- description: detailed explanation of the problem and why it matters
- quote: the exact text from the manuscript that contains or demonstrates the issue
- location: which section (introduction, methods, results, discussion)
- severity: one of [critical, major, moderate, minor]

Return ONLY a JSON object: {"issues": [...]}

Be thorough. Look for anything that affects the validity, replicability, or interpretation of the findings.

--- MANUSCRIPT ---
{paper_text}"""
