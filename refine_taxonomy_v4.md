# Refine.ink Issue Taxonomy v4
## For Integration with Evidence.Guide Replication Prediction Model

**Version:** 4.0  
**Date:** January 13, 2026  
**Status:** v4 draft

---

## Design Principles

1. **Paper-only detection**: All categories must be detectable from reading the manuscript alone (no external data required)
2. **No overlap with Evidence.Guide**: Excludes statcheck, GRIM/DEBIT, p-curve, effect size extraction, preregistration fidelity comparison
3. **Replication-predictive**: Categories weighted by empirical evidence linking them to replication failure
4. **Honest framing**: Categories describe what's observable, not what's inferred

---

## Full Taxonomy (10 Categories, 62 Subcategories)

### CATEGORY 1: STATISTICAL ERRORS
*Detectable computational mistakes in reported statistics*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `calculation_mismatch` | Reported values don't compute from given inputs | Manual recalculation |
| `df_error` | Degrees of freedom inconsistent with design/N | Check df against N and design |
| `test_parameter_error` | Wrong test for design, wrong parameters reported | Match test to design |
| `table_data_error` | Values in tables inconsistent or misplaced | Cross-check tables |

**Replication Relevance: HIGH**  
*Nuijten et al.: 12.5% of papers have gross inconsistencies that change significance*

---

### CATEGORY 2: METHODOLOGICAL DESIGN
*Threats to internal validity from study design choices*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `pooling_heterogeneous_data` | Combining data across different procedures without justification | Check if pooled analyses mix distinct methods |
| `multiple_comparisons_uncorrected` | Many tests without correction or acknowledgment | Count tests, check for correction |
| `randomization_unclear` | Random assignment claimed but procedure not described | Check methods for sequence generation |
| `underpowered_subgroups` | Subgroup analyses with very small cell sizes | Check Ns in subgroup analyses |
| `missing_key_analysis` | Obvious analysis omitted (e.g., no main effects reported) | Compare design to reported analyses |
| `blinding_inadequate` | Assessors/participants unblinded when blinding was feasible | Check blinding description |
| `allocation_concealment_unclear` | Randomization not protected from foreknowledge | Check if allocation was concealed |
| `demand_characteristics_likely` | Design allows participants to guess hypothesis | Assess transparency of manipulation |
| `control_condition_inadequate` | Control doesn't isolate manipulation (active placebo issues) | Evaluate control appropriateness |
| `measurement_timing_problematic` | Assessment at wrong timepoint for construct | Check measurement timing logic |

**Replication Relevance: HIGH**  
*RoB meta-epidemiology: inadequate allocation concealment inflates effects 25-40%*

---

### CATEGORY 3: CONSTRUCT VALIDITY
*Problems with whether the study measures/manipulates what it claims*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `manipulation_spillover` | Induction affects unintended constructs | Check manipulation checks for other emotions/states |
| `measure_conflation` | DV mixes distinct processes (e.g., behavior + luck) | Analyze what DV actually captures |
| `construct_operationalization_mismatch` | Measure doesn't match construct definition | Compare operationalization to construct |
| `confound_with_alternative_construct` | Effect could be due to related but distinct construct | Identify plausible alternative constructs |

**Replication Relevance: HIGH**  
*If not measuring X, "effect of X" won't replicate as claimed*

---

### CATEGORY 4: CAUSAL INFERENCE
*Problems with causal claims beyond design*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `mechanism_unmeasured` | Causal mechanism claimed but mediator not measured | Check if mediating variables assessed |
| `causal_chain_incomplete` | Only some links in proposed chain tested | Map claimed chain to actual tests |
| `correlation_causation_conflation` | Causal language for correlational design | Match claims to design type |
| `reverse_causation_unaddressed` | Plausible reverse direction not discussed | Consider alternative causal directions |
| `confound_unaddressed` | Obvious third variable not discussed | Identify uncontrolled confounds |
| `temporal_precedence_unclear` | IV may not precede DV | Check temporal ordering |
| `third_variable_likely` | Plausible common cause not acknowledged | Identify potential common causes |

**Replication Relevance: MEDIUM**  
*Effect may replicate even if causal interpretation is wrong*

---

### CATEGORY 5: INTERNAL CONSISTENCY
*Contradictions within the manuscript*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `cross_section_contradiction` | Intro claims contradict discussion claims | Compare sections |
| `cross_experiment_heterogeneity` | Different experiments show different patterns | Compare results across studies |
| `statistic_text_table_mismatch` | Numbers in text don't match tables | Cross-reference text and tables |
| `definition_inconsistency` | Term used differently in different sections | Track term usage |

**Replication Relevance: MEDIUM**  
*Contradictions suggest post-hoc interpretation or errors*

---

### CATEGORY 6: REPORTING COMPLETENESS
*Missing information that limits evaluation or replication*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `missing_parameters` | Can't verify computation (missing df, N, etc.) | Check for complete statistical reporting |
| `unclear_procedure` | Procedure not described in replicable detail | Assess procedural completeness |
| `missing_subgroup_data` | Subgroups mentioned but data not shown | Check if all mentioned analyses reported |
| `incomplete_manipulation_check` | Manipulation check missing or incomplete | Check for manipulation verification |
| `intervention_not_replicable` | Insufficient detail to reproduce intervention | Could someone replicate from description? |
| `materials_not_available` | Stimuli/measures not provided or accessible | Check for materials access |
| `participant_flow_unclear` | Can't reconstruct N through study phases | Check for flow diagram / attrition accounting |
| `primary_outcome_not_specified` | No clear hierarchy among outcomes | Check for primary outcome designation |
| `analysis_plan_absent` | No indication of pre-specification | Look for analysis plan reference |

**Replication Relevance: MEDIUM**  
*Limits ability to assess or attempt replication*

---

### CATEGORY 7: GENERALIZABILITY
*Overclaims about external validity*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `external_validity_overclaim` | Claims extend beyond what design supports | Compare claims to sample/context |
| `context_dependent_unacknowledged` | Effect likely context-specific but not noted | Assess generalization assumptions |
| `sample_limitation_unaddressed` | Sample constraints not discussed | Check limitations section |
| `ecological_validity_assumption` | Lab task assumed to map to real behavior | Assess task-to-world inference |

**Replication Relevance: LOW**  
*About interpretation scope, not whether effect exists*

---

### CATEGORY 8: THEORETICAL / CONCEPTUAL
*Problems with theoretical framing and terminology*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `term_misuse` | Established term used non-standardly | Check term against standard usage |
| `framework_misapplication` | Theory applied incorrectly | Assess theory application |
| `classification_error` | Construct placed in wrong category | Check classification against literature |
| `citation_error` | Malformed or incorrect citation | Verify citation accuracy |

**Replication Relevance: LOW**  
*Writing/framing quality, not effect validity*

---

### CATEGORY 9: ANALYTIC FLEXIBILITY / TRANSPARENCY
*Indicators of opportunity for or occurrence of selective analysis*

**Important framing note:** These are *risk indicators* detectable from the paper, not proof of selective reporting. They create opportunity for or suggest possible selective analysis.

#### Opportunity Indicators
*Features that create room for analytic flexibility*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `many_dvs_no_primary` | Multiple outcomes without designated primary or correction | Count DVs, check for hierarchy |
| `complex_design_incomplete_reporting` | Not all cells/conditions accounted for in results | Compare design matrix to results |
| `vague_exclusion_criteria` | Exclusions could be applied flexibly | Check if criteria specific and pre-stated |
| `covariate_justification_absent` | Controls included without rationale | Check if covariates explained |
| `subgroup_analyses_unmarked` | Exploratory subgroups presented without acknowledgment | Check if subgroups flagged as exploratory |

#### Suspiciously Clean Patterns
*Results patterns that are improbable under honest reporting*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `all_predictions_confirmed` | Every hypothesis supported, no disconfirmations | Count confirmed vs. disconfirmed |
| `no_null_results` | No non-significant findings reported anywhere | Look for any p > .05 |
| `interaction_without_main_effects` | Complex moderation but simpler effects absent | Check for main effects when interactions reported |

#### HARKing Language Patterns
*Linguistic signals of post-hoc hypothesis construction*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `harking_language` | Post-hoc framing presented as a priori | Detect "as predicted" for complex specific patterns |
| `hypothesis_specificity_mismatch` | Vague intro hypothesis, specific discussion interpretation | Compare intro precision to discussion precision |
| `results_dependent_framing` | Theoretical framing tracks results too closely | Assess whether theory follows data |

**Replication Relevance: CRITICAL**  
*QRP surveys: 63% admit to not reporting all DVs; Simmons et al.: combining 4 flexibilities inflates false positives from 5% to 61%*

---

### CATEGORY 10: ATTRITION / MISSING DATA
*Problems with participant loss and missing data handling*

| Subcategory | Description | Detection Method |
|-------------|-------------|------------------|
| `differential_attrition` | Dropout rate differs by condition | Compare attrition across conditions |
| `high_overall_attrition` | >20% dropout without justification | Calculate overall attrition rate |
| `missing_data_handling_unclear` | No description of how missingness addressed | Check for missing data approach |
| `per_protocol_only` | No ITT analysis when appropriate | Check if ITT conducted |
| `attrition_not_by_condition` | Can't assess differential dropout from report | Check if attrition broken down by condition |

**Replication Relevance: HIGH**  
*RoB 2 core domain; differential attrition can invalidate RCT conclusions*

---

## Replication Relevance Summary

| Category | Risk Level | Empirical Basis |
|----------|------------|-----------------|
| **9. Analytic Flexibility** | CRITICAL | QRP surveys + Simmons false positive simulations |
| **1. Statistical Errors** | HIGH | Nuijten: 12.5% gross inconsistencies |
| **2. Methodological Design** | HIGH | RoB meta-epidemiology: 25-40% inflation |
| **10. Attrition/Missing Data** | HIGH | RoB 2 core domain |
| **3. Construct Validity** | HIGH | Measurement ≠ construct → won't replicate |
| **4. Causal Inference** | MEDIUM | Effect may replicate with wrong mechanism |
| **5. Internal Consistency** | MEDIUM | Contradictions suggest post-hoc |
| **6. Reporting Completeness** | MEDIUM | Limits assessment, not validity per se |
| **7. Generalizability** | LOW | Interpretation scope, not existence |
| **8. Theoretical/Conceptual** | LOW | Writing quality |

---

## JSON Schema for Refine.ink Output

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RefineInkQualityAssessment",
  "description": "Structured output from Refine.ink for Evidence.Guide integration",
  "type": "object",
  "required": ["paper_id", "refine_version", "assessment_date", "summary_scores", "issue_counts", "replication_risk_indicators"],
  
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "DOI or unique identifier"
    },
    "refine_version": {
      "type": "string",
      "description": "Refine.ink version used"
    },
    "assessment_date": {
      "type": "string",
      "format": "date-time"
    },
    
    "summary_scores": {
      "type": "object",
      "description": "0-1 scores for major quality dimensions",
      "properties": {
        "overall_quality": { "type": "number", "minimum": 0, "maximum": 1 },
        "statistical_rigor": { "type": "number", "minimum": 0, "maximum": 1 },
        "methodological_soundness": { "type": "number", "minimum": 0, "maximum": 1 },
        "construct_validity": { "type": "number", "minimum": 0, "maximum": 1 },
        "causal_inference_quality": { "type": "number", "minimum": 0, "maximum": 1 },
        "internal_consistency": { "type": "number", "minimum": 0, "maximum": 1 },
        "reporting_completeness": { "type": "number", "minimum": 0, "maximum": 1 },
        "analytic_transparency": { "type": "number", "minimum": 0, "maximum": 1 }
      },
      "required": ["overall_quality"]
    },
    
    "issue_counts": {
      "type": "object",
      "description": "Count of issues by category",
      "properties": {
        "statistical_errors": { "type": "integer", "minimum": 0 },
        "methodological_design": { "type": "integer", "minimum": 0 },
        "construct_validity": { "type": "integer", "minimum": 0 },
        "causal_inference": { "type": "integer", "minimum": 0 },
        "internal_consistency": { "type": "integer", "minimum": 0 },
        "reporting_completeness": { "type": "integer", "minimum": 0 },
        "generalizability": { "type": "integer", "minimum": 0 },
        "theoretical_conceptual": { "type": "integer", "minimum": 0 },
        "analytic_flexibility": { "type": "integer", "minimum": 0 },
        "attrition_missing_data": { "type": "integer", "minimum": 0 }
      }
    },
    
    "issue_counts_by_risk_level": {
      "type": "object",
      "description": "Issues aggregated by replication risk level",
      "properties": {
        "critical": { "type": "integer", "minimum": 0, "description": "Analytic flexibility issues" },
        "high": { "type": "integer", "minimum": 0, "description": "Statistical, methodological, attrition, construct validity" },
        "medium": { "type": "integer", "minimum": 0, "description": "Causal, consistency, reporting" },
        "low": { "type": "integer", "minimum": 0, "description": "Generalizability, theoretical" }
      }
    },
    
    "replication_risk_indicators": {
      "type": "object",
      "description": "Boolean flags for specific high-risk patterns",
      "properties": {
        "all_predictions_confirmed": { "type": "boolean" },
        "no_null_results_reported": { "type": "boolean" },
        "many_dvs_no_primary_designated": { "type": "boolean" },
        "complex_design_incomplete_reporting": { "type": "boolean" },
        "harking_language_detected": { "type": "boolean" },
        "differential_attrition_present": { "type": "boolean" },
        "cross_experiment_heterogeneity": { "type": "boolean" },
        "mechanism_claimed_not_measured": { "type": "boolean" },
        "construct_confound_identified": { "type": "boolean" },
        "blinding_inadequate_or_unclear": { "type": "boolean" },
        "subgroup_analyses_unmarked_exploratory": { "type": "boolean" }
      }
    },
    
    "derived_features": {
      "type": "object",
      "description": "Computed features for model input",
      "properties": {
        "total_issues": { "type": "integer", "minimum": 0 },
        "critical_issue_density": { 
          "type": "number", 
          "description": "critical_issues / total_issues" 
        },
        "high_risk_issue_density": { 
          "type": "number", 
          "description": "(critical + high) / total_issues" 
        },
        "flexibility_indicator_count": {
          "type": "integer",
          "description": "Sum of boolean risk indicators that are true"
        }
      }
    },
    
    "issues": {
      "type": "array",
      "description": "Detailed list of all identified issues",
      "items": {
        "type": "object",
        "required": ["id", "category", "subcategory", "severity", "replication_relevant"],
        "properties": {
          "id": { "type": "string" },
          "category": { 
            "type": "string",
            "enum": [
              "statistical_errors",
              "methodological_design", 
              "construct_validity",
              "causal_inference",
              "internal_consistency",
              "reporting_completeness",
              "generalizability",
              "theoretical_conceptual",
              "analytic_flexibility",
              "attrition_missing_data"
            ]
          },
          "subcategory": { "type": "string" },
          "severity": {
            "type": "string",
            "enum": ["critical", "major", "moderate", "minor"],
            "description": "Issue-level severity within category"
          },
          "replication_relevant": {
            "type": "boolean",
            "description": "True if issue likely affects replicability"
          },
          "quote": {
            "type": "string",
            "description": "Relevant text from manuscript"
          },
          "feedback": {
            "type": "string", 
            "description": "Explanation of the issue"
          },
          "location": {
            "type": "string",
            "description": "Section of paper (intro, methods, results, discussion)"
          }
        }
      }
    },
    
    "overall_feedback": {
      "type": "string",
      "description": "High-level summary narrative"
    }
  }
}
```

---

## Example Output (Anger/Risk-Taking Paper)

```json
{
  "paper_id": "doi:10.1234/example",
  "refine_version": "2.0",
  "assessment_date": "2026-01-13T20:33:18Z",
  
  "summary_scores": {
    "overall_quality": 0.62,
    "statistical_rigor": 0.75,
    "methodological_soundness": 0.58,
    "construct_validity": 0.48,
    "causal_inference_quality": 0.42,
    "internal_consistency": 0.55,
    "reporting_completeness": 0.70,
    "analytic_transparency": 0.50
  },
  
  "issue_counts": {
    "statistical_errors": 1,
    "methodological_design": 2,
    "construct_validity": 3,
    "causal_inference": 2,
    "internal_consistency": 4,
    "reporting_completeness": 1,
    "generalizability": 2,
    "theoretical_conceptual": 3,
    "analytic_flexibility": 2,
    "attrition_missing_data": 0
  },
  
  "issue_counts_by_risk_level": {
    "critical": 2,
    "high": 6,
    "medium": 7,
    "low": 5
  },
  
  "replication_risk_indicators": {
    "all_predictions_confirmed": false,
    "no_null_results_reported": false,
    "many_dvs_no_primary_designated": false,
    "complex_design_incomplete_reporting": false,
    "harking_language_detected": false,
    "differential_attrition_present": false,
    "cross_experiment_heterogeneity": true,
    "mechanism_claimed_not_measured": true,
    "construct_confound_identified": true,
    "blinding_inadequate_or_unclear": false,
    "subgroup_analyses_unmarked_exploratory": false
  },
  
  "derived_features": {
    "total_issues": 20,
    "critical_issue_density": 0.10,
    "high_risk_issue_density": 0.40,
    "flexibility_indicator_count": 3
  },
  
  "issues": [
    {
      "id": "issue_001",
      "category": "construct_validity",
      "subcategory": "manipulation_spillover",
      "severity": "major",
      "replication_relevant": true,
      "quote": "the anger induction also increased sadness to some extent",
      "feedback": "The anger manipulation affected sadness, making it unclear whether effects are anger-specific or general negative affect",
      "location": "results"
    },
    {
      "id": "issue_002", 
      "category": "construct_validity",
      "subcategory": "measure_conflation",
      "severity": "major",
      "replication_relevant": true,
      "quote": "combines behavioral choices (adjusted average pumps) with outcomes (total earnings)",
      "feedback": "DV mixes controllable behavior with stochastic luck; behavioral metric should be isolated",
      "location": "methods"
    },
    {
      "id": "issue_003",
      "category": "causal_inference", 
      "subcategory": "mechanism_unmeasured",
      "severity": "major",
      "replication_relevant": true,
      "quote": "anger triggers certainty/control appraisals... which in turn increase risk-taking",
      "feedback": "Causal mechanism claimed but mediating variables (appraisals, motives) not measured",
      "location": "discussion"
    },
    {
      "id": "issue_004",
      "category": "internal_consistency",
      "subcategory": "cross_experiment_heterogeneity", 
      "severity": "moderate",
      "replication_relevant": true,
      "quote": "Experiment 1 demonstrates a main effect... Experiments 2 and 3 drive the central claim of a gender interaction",
      "feedback": "Pattern shifts across experiments; main effect in Exp 1 vs. interaction in Exps 2-3 raises stability concerns",
      "location": "results"
    }
  ],
  
  "overall_feedback": "The manuscript presents three experiments examining gender differences in anger-driven risk-taking. Key concerns include: (1) construct validity issues with anger induction also affecting sadness, suggesting effects may reflect general negative affect rather than anger-specific mechanisms; (2) the composite DV conflates behavior with luck-based outcomes; (3) causal mechanisms are claimed but mediators not measured; (4) the pattern of results shifts notably between Experiment 1 (main effect) and Experiments 2-3 (interaction), raising questions about stability. Statistical reporting is generally adequate but several internal inconsistencies were identified."
}
```

---

## Mapping to Evidence.Guide Pipeline

### Integration Points

| Refine Output | Evidence.Guide Usage |
|---------------|---------------------|
| `summary_scores.*` | Direct features for scoring model |
| `issue_counts_by_risk_level.*` | Weighted issue counts |
| `replication_risk_indicators.*` | Boolean feature flags |
| `derived_features.flexibility_indicator_count` | Key predictor variable |
| `derived_features.high_risk_issue_density` | Normalized risk score |

### Combined Feature Vector (per paper)

```
Evidence.Guide features:
- p_value_extracted
- effect_size_d
- sample_size
- preregistered (bool)
- prereg_fidelity_score
- grim_flags
- statcheck_errors
- p_curve_z

Refine features:
- overall_quality_score
- analytic_transparency_score
- critical_issue_count
- high_risk_issue_density
- flexibility_indicator_count
- mechanism_claimed_not_measured (bool)
- construct_confound_identified (bool)
- cross_experiment_heterogeneity (bool)
```

---

## Open Questions

1. **Granularity**: Does Refine output at subcategory level, or would category-level aggregation be more reliable?

2. **Score calibration**: How are the 0-1 summary scores derived? Are they calibrated across papers?

3. **Detection reliability**: Which subcategories can Refine detect reliably vs. which need explicit prompting?

4. **Batch consistency**: Does Refine produce consistent assessments when run multiple times on the same paper?

5. **Training signal**: For model training, should we use the boolean risk indicators, the continuous scores, or both?
