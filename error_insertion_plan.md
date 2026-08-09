# Error Insertion Plan for AI Peer Review Benchmarking

## Overview

100 deeply structural errors inserted across 10 papers (10 per paper), one per taxonomy category per paper. Each error targets a **load-bearing methodological element** — the kind of issue only an expert reviewer with domain knowledge would catch.

## Design Philosophy: Deep, Not Shallow

These errors are NOT surface-level word changes ("suggest" → "demonstrate") or added overclaiming sentences. They are **structural modifications** that undermine the paper's conclusions by removing or altering the specific methodological safeguards that protect them:

- **Deleting manipulation checks** that rule out alternative explanations (e.g., removing response bias analysis, confound checks)
- **Changing sample descriptions** from representative to convenience (e.g., NZ nationally representative N=22,974 → university students N=374)
- **Removing model specifications** that are essential for validity (e.g., deleting measurement invariance, autoregressive controls, random effects)
- **Swapping theoretical constructs** in ways that create theory-operationalization mismatches (e.g., affect heuristic → availability heuristic)
- **Reversing procedure timing** that changes the cognitive mechanism being tested (e.g., post- to pre-misinformation interventions)
- **Removing counterbalancing** that prevents item confounds in within-subjects designs
- **Changing construct formulas** to collapse key theoretical distinctions (e.g., P(category|suffix) → P(suffix|category))
- **Deleting sensitivity analyses** that confirmed robustness under alternative specifications
- **Removing pre-registration details** that constrain analytic flexibility

Most modified papers are SHORTER than originals (negative char deltas) because the errors often involve removing protective methodological elements rather than adding text. Perfectly 10 per category across all 10 papers.

## Coverage Summary

| Category | Count | Subcategories |
|----------|-------|---------------|
| analytic_flexibility | 6 | complex_design_incomplete_reporting, covariate_justification_absent, interaction_without_main_effects, many_dvs_no_primary, subgroup_analyses_unmarked, vague_exclusion_criteria |
| attrition_missing_data | 5 | attrition_not_by_condition, differential_attrition, high_overall_attrition, missing_data_handling_unclear, per_protocol_only |
| causal_inference | 7 | causal_chain_incomplete, confound_unaddressed, correlation_causation_conflation, mechanism_unmeasured, reverse_causation_unaddressed, temporal_precedence_unclear, third_variable_likely |
| construct_validity | 4 | confound_with_alternative_construct, construct_operationalization_mismatch, manipulation_spillover, measure_conflation |
| generalizability | 4 | context_dependent_unacknowledged, ecological_validity_assumption, external_validity_overclaim, sample_limitation_unaddressed |
| internal_consistency | 4 | cross_experiment_heterogeneity, cross_section_contradiction, definition_inconsistency, statistic_text_table_mismatch |
| methodological_design | 8 | allocation_concealment_unclear, blinding_inadequate, control_condition_inadequate, demand_characteristics_likely, measurement_timing_problematic, multiple_comparisons_uncorrected, randomization_unclear, underpowered_subgroups |
| reporting_completeness | 5 | missing_parameters, missing_subgroup_data, participant_flow_unclear, primary_outcome_not_specified, unclear_procedure |
| statistical_errors | 4 | calculation_mismatch, df_error, table_data_error, test_parameter_error |
| theoretical_conceptual | 3 | classification_error, framework_misapplication, term_misuse |

## Per-Paper Error Inventory

### Paper 1

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | causal_inference | correlation_causation_conflation | Changed hedged 'suggest that there is' to definitive 'demonstrate', overstating causal claims from c |
| 2 | generalizability | external_validity_overclaim | Overclaims generalizability from single-country (NZ) sample to all Western democracies |
| 3 | reporting_completeness | missing_parameters | Removed CFI=.86 and SRMR=.07, omitting key fit indices (notably CFI below .90 threshold) |
| 4 | attrition_missing_data | missing_data_handling_unclear | Changed robust FIML to listwise deletion, inappropriate for longitudinal study with substantial attr |
| 5 | causal_inference | temporal_precedence_unclear | Changed hedged 'suggest'/'stronger influence' to definitive 'confirm'/'causal influence', overstatin |
| 6 | causal_inference | reverse_causation_unaddressed | Falsely claims reverse path was non-significant when authors explicitly reported it was significant |
| 7 | generalizability | sample_limitation_unaddressed | Replaced specific ethnic composition (86% Pakeha) with vague 'diverse' claim, hiding monoethnic samp |
| 8 | reporting_completeness | unclear_procedure | Removed disclosure that one RWA item was missing at time two, hiding measurement inconsistency acros |
| 9 | attrition_missing_data | high_overall_attrition | Added 'who completed all five waves' implying zero attrition over 5 years, which is implausible |
| 10 | statistical_errors | test_parameter_error | Changed p from <.001 to .032 -- chi-square of 50.98 with df=1 yields p far below .001 |

### Paper 2

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | construct_validity | manipulation_spillover | Added sentence obscuring manipulation spillover risk from merging separate studies |
| 2 | statistical_errors | calculation_mismatch | Changed d from 0.41 to 0.51 but left CI unchanged -- CI no longer consistent with point estimate |
| 3 | analytic_flexibility | many_dvs_no_primary | Expanded DVs to 8+ without designating primary outcome, creating multiple comparisons problem |
| 4 | internal_consistency | cross_experiment_heterogeneity | Mischaracterizes Study 1 medium effects as 'large', creating cross-study inconsistency |
| 5 | construct_validity | construct_operationalization_mismatch | Added 'hypothetically' and 'Likert scale', changing concrete dollar amount to vague attitudinal rati |
| 6 | statistical_errors | table_data_error | Changed p from .041 to .004, inconsistent with t=2.47 at df=994 |
| 7 | analytic_flexibility | subgroup_analyses_unmarked | Added unmarked gender subgroup analysis not in pre-registered plan |
| 8 | reporting_completeness | unclear_procedure | Removed 'randomly', making assignment procedure unclear for between-subjects design |
| 9 | causal_inference | correlation_causation_conflation | Changed 'correlated strongly with' to 'drove', implying causation from correlation |
| 10 | methodological_design | measurement_timing_problematic | Changed power from 0.95 to 0.80 but left N=314 unchanged -- inconsistent with power calculation |

### Paper 3

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | theoretical_conceptual | term_misuse | Swapped 'cognitive niche' for 'cultural niche' hypothesis -- these are distinct frameworks the paper |
| 2 | theoretical_conceptual | framework_misapplication | Replaced cognitive mechanism with cultural transmission mechanism, misattributing cultural niche cla |
| 3 | methodological_design | demand_characteristics_likely | Added disclosure of study purpose, introducing demand characteristics |
| 4 | construct_validity | confound_with_alternative_construct | Changed unfamiliarity claim to acknowledge prior knowledge, undermining key construct validity argum |
| 5 | internal_consistency | cross_experiment_heterogeneity | Reversed conclusion from 'do not provide support' to 'provide partial support', contradicting report |
| 6 | methodological_design | control_condition_inadequate | Moved 'associated scores' from control to treatment condition, making conditions differ on two dimen |
| 7 | internal_consistency | cross_section_contradiction | Changed prediction to say understanding WILL improve, contradicting results and cultural niche frame |
| 8 | internal_consistency | statistic_text_table_mismatch | Changed mean from 4.47 to 5.12, contradicting 'remained the same' narrative and inconsistent with HP |
| 9 | internal_consistency | definition_inconsistency | Changed 'smaller' to 'larger' moment of inertia while keeping same parenthetical definition, creatin |
| 10 | analytic_flexibility | vague_exclusion_criteria | Changed 'last two trials' to 'best two trials', cherry-picking optimal performance |

### Paper 4

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | reporting_completeness | missing_parameters | Removed screening numbers (2377 online, 77 phone), hiding selection funnel |
| 2 | attrition_missing_data | high_overall_attrition | Replaced specific breakdown (15/12) with vague 'most/remaining', hiding 45% attrition from key condi |
| 3 | statistical_errors | test_parameter_error | Changed p-values from .277-.285 to .077-.085, making non-significant results appear marginally signi |
| 4 | causal_inference | confound_unaddressed | Inserted causal/predictive claim about language markers from retrospective design |
| 5 | reporting_completeness | unclear_procedure | Removed SMS download step, obscuring temporal order of data access and episode identification |
| 6 | reporting_completeness | primary_outcome_not_specified | Changed 'three previously discussed constructs' to 'all LIWC categories', removing pre-specified pri |
| 7 | attrition_missing_data | missing_data_handling_unclear | Added inappropriate imputation claim that would bias results and contradicts mixed-effects approach |
| 8 | causal_inference | third_variable_likely | Inserted causal precursor claim from correlational within-subjects design, ignoring third variables |
| 9 | methodological_design | control_condition_inadequate | Removed positive mood baseline condition, preventing distinction of suicidal vs. general negative af |
| 10 | analytic_flexibility | covariate_justification_absent | Claims Bonferroni was applied when it wasn't -- results at p<.05 wouldn't survive correction; also m |

### Paper 5

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | attrition_missing_data | differential_attrition | Removed specific exclusion count (5), preventing evaluation of attrition pattern |
| 2 | methodological_design | allocation_concealment_unclear | Replaced candid admission of unknown procedures with false claim of consistency |
| 3 | analytic_flexibility | vague_exclusion_criteria | Removed disclosure that SAU replication ran participants in groups of 2-6, hiding procedural deviati |
| 4 | generalizability | context_dependent_unacknowledged | Flipped explicit limitation about small k into false claim of robustness |
| 5 | attrition_missing_data | per_protocol_only | Added unstated per-protocol exclusion of 23 participants without reporting enrollment-to-analysis fl |
| 6 | attrition_missing_data | attrition_not_by_condition | Added unsupported claim that attrition was comparable across sites without providing figures |
| 7 | methodological_design | blinding_inadequate | Inserted false claim of blinded procedure for self-report questionnaire about Facebook/self-esteem |
| 8 | methodological_design | randomization_unclear | Added false claim of random assignment to lab vs. online when likely self-selected |
| 9 | reporting_completeness | participant_flow_unclear | Added misleading claim that reported N represents all enrolled participants |
| 10 | analytic_flexibility | subgroup_analyses_unmarked | Inserted unmarked post-hoc median split subgroup analysis without correction |

### Paper 6

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | causal_inference | mechanism_unmeasured | Changed hedged language to definitive causal claims, overstating what autoregressive design establis |
| 2 | methodological_design | measurement_timing_problematic | Changed 'sufficient'/'will not differ' to 'optimal'/'typically stronger', misrepresenting cited lite |
| 3 | internal_consistency | cross_section_contradiction | Changed exclusion count from 78 to 24, creating arithmetic inconsistency with reported final N=372 |
| 4 | attrition_missing_data | missing_data_handling_unclear | Removed breakdown showing 45% of missing data was out-of-range responses, hiding measurement problem |
| 5 | causal_inference | causal_chain_incomplete | Upgraded correlational language to causal ('related to' -> 'cause', 'suggested as' -> 'established a |
| 6 | causal_inference | confound_unaddressed | Replaced factual comparison with unsubstantiated claim gender won't confound results (96.64% far exc |
| 7 | internal_consistency | definition_inconsistency | Removed secondary trauma component from definition, inconsistent with measure used and later descrip |
| 8 | theoretical_conceptual | framework_misapplication | Added 'directly produce'/'deterministically lead to', removing cognitive appraisal component central |
| 9 | attrition_missing_data | differential_attrition | Added unsupported claim that 94 exclusions were evenly distributed across incivility levels |
| 10 | analytic_flexibility | subgroup_analyses_unmarked | Inserted unmarked post-hoc tenure subgroup analysis without exploratory flag or correction |

### Paper 7

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | statistical_errors | calculation_mismatch | Changed 7%/26% to 9%/28%, arithmetic no longer consistent with figures |
| 2 | methodological_design | underpowered_subgroups | Added false power claim for n=23 after losing 42.5% of participants to exclusion |
| 3 | analytic_flexibility | interaction_without_main_effects | Changed BF from 4.84 to 0.84, undermining interaction interpretation |
| 4 | internal_consistency | cross_experiment_heterogeneity | Omitted Experiment 4 from summary, inconsistent with General Discussion |
| 5 | statistical_errors | df_error | Changed included from 91 to 89 while keeping 4 excluded -- no longer sums to 95 |
| 6 | statistical_errors | table_data_error | Changed BFincl from 206 to 260, creating text-table mismatch (Table 2 reports 206.37) |
| 7 | methodological_design | multiple_comparisons_uncorrected | Added six uncorrected follow-up t-tests with no multiplicity correction |
| 8 | analytic_flexibility | complex_design_incomplete_reporting | Added statement omitting main effects from factorial ANOVA, incomplete design reporting |
| 9 | internal_consistency | statistic_text_table_mismatch | Changed BFincl from 4.21 to 14.21, mismatching Table 1 value of 4.205 |
| 10 | reporting_completeness | unclear_procedure | Removed counterbalanced manipulation of response options, confounding illusions with response availa |

### Paper 8

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | methodological_design | control_condition_inadequate | Changed control to memory-accuracy content, which could itself reduce memory conformity |
| 2 | methodological_design | demand_characteristics_likely | Weakened exclusion criterion from 'our hypotheses' to 'general topic of memory research' |
| 3 | reporting_completeness | missing_subgroup_data | Added testing pairwise comparisons without significant omnibus, inflating Type I error |
| 4 | generalizability | external_validity_overclaim | Changed 'closer to real life' to 'directly applicable to forensic settings' |
| 5 | methodological_design | blinding_inadequate | Added statement that experimenter is unblinded during outcome measurement |
| 6 | construct_validity | construct_operationalization_mismatch | Emphasized forgetting-type sins instead of suggestibility/misattribution, mismatching target constru |
| 7 | construct_validity | measure_conflation | Conflated misinformation-consistent errors with general errors, making conformity indistinguishable |
| 8 | reporting_completeness | unclear_procedure | Added unspecified experimenter Q&A that could compromise MORI deception |
| 9 | statistical_errors | calculation_mismatch | Changed Cohen f from 0.57 to 0.80 -- g=1.13 converts to f=d/2=0.565, not 0.80 |
| 10 | analytic_flexibility | complex_design_incomplete_reporting | Added uncorrected alpha for 6 pairwise comparisons, inflating family-wise error to ~.26 |

### Paper 9

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | generalizability | external_validity_overclaim | Changed 'strong' to 'definitive', removed 'self-reported', added causal claim from cross-sectional d |
| 2 | causal_inference | correlation_causation_conflation | Weakened clear causal limitation, conflating correlation with causation |
| 3 | theoretical_conceptual | classification_error | Replaced validation caveat with contested classification claim |
| 4 | causal_inference | third_variable_likely | Changed moderation description to causal pathway claim, ignoring third variables |
| 5 | generalizability | ecological_validity_assumption | Claims online surveys approximate real-world dynamics, conflating survey convenience with ecological |
| 6 | generalizability | sample_limitation_unaddressed | Added unsupported equivalence/unbiased claim for unvalidated cross-domain measurement |
| 7 | theoretical_conceptual | framework_misapplication | Misapplies equivalence testing by claiming null equivalence = no causal role (only addresses effect  |
| 8 | methodological_design | multiple_comparisons_uncorrected | Claims no correction needed for 10 tests because 'distinct hypotheses' -- doesn't account for correl |
| 9 | internal_consistency | cross_section_contradiction | Claims all 4000 are nationally representative, contradicting prior sentence about 1500 sports-wageri |
| 10 | reporting_completeness | missing_parameters | Silently dropped third NIDA-ASSIST item (functional impairment) and changed count from three to two |

### Paper 10

| # | Category | Subcategory | Description |
|---|----------|-------------|-------------|
| 1 | statistical_errors | calculation_mismatch | Changed token correlation from 0.47 to 0.57, contradicting pattern that type > token |
| 2 | statistical_errors | test_parameter_error | Changed df from 2 to 1, inconsistent with two parameters added |
| 3 | theoretical_conceptual | term_misuse | Changed 'preferred' to 'exclusive', misdefining graded measure as binary |
| 4 | analytic_flexibility | many_dvs_no_primary | Framed all 6 DVs as equally important without primary designation |
| 5 | analytic_flexibility | covariate_justification_absent | Added unjustified covariates (nonword length, neighbourhood size) without rationale |
| 6 | methodological_design | control_condition_inadequate | Changed 'one suffix only' to 'one or two', breaking design that prevents priming effects |
| 7 | construct_validity | construct_operationalization_mismatch | Changed range from '0 to 1' to '-1 to 1', impossible for count-based ratio |
| 8 | internal_consistency | cross_section_contradiction | Changed 'slightly different' to 'matched' while stats show significant difference (p<.05) |
| 9 | generalizability | external_validity_overclaim | Replaced hedged 'further research needed' with overclaimed universality from single-language study |
| 10 | reporting_completeness | missing_parameters | Changed 'did not show an effect' to 'marginal effect' while p>0.8 is clearly null |

## Evaluation Protocol

Each AI peer review system is evaluated against the 100 inserted errors:
- **Per-paper score**: X/10 errors detected
- **Per-category score**: X/N errors detected per taxonomy category
- **Overall score**: X/100 errors detected
- **False positive rate**: issues flagged that don't correspond to inserted errors (evaluated against original papers)

## Files

- `original papers/` — Unmodified manuscripts (ground truth)
- `modified papers/` — Manuscripts with errors inserted
- `error_insertions.csv` — Full details of all 100 errors (paper, category, subcategory, original text, modified text, description)
