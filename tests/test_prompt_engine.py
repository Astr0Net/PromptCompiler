import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt_compiler.catalog import KNOWN_CATEGORIES
from prompt_compiler.prompt_engine import SYSTEM_PROMPT, parse_model_output


class SystemPromptPolicyTests(unittest.TestCase):
    """The compiled-system prompt must enforce a strict requirement-preservation policy."""

    REQUIRED_CATEGORIES = {
        "coding", "debugging", "research", "writing", "image_generation",
        "translation", "data_analysis", "planning", "automation", "general",
    }

    def test_contains_requirement_integrity_policy(self):
        self.assertIn("Requirement Integrity Policy", SYSTEM_PROMPT)

    def test_does_not_encourage_follow_up_filling(self):
        # The biggest existing bug: this phrasing encourages the model to
        # invent missing requirements. It must be gone.
        self.assertNotIn(
            "comprehensive enough that an AI agent can execute it without asking follow-up questions",
            SYSTEM_PROMPT,
        )

    def test_contains_anti_hallucination_rules(self):
        checks = [
            "NEVER invent requirements",
            "NEVER fabricate technical specifications",
            "NEVER add technologies simply because they are considered",
            "NEVER convert optional recommendations into mandatory requirements",
            "NEVER silently resolve important ambiguities by guessing",
        ]
        for phrase in checks:
            self.assertIn(phrase, SYSTEM_PROMPT, f"missing: {phrase}")

    def test_contains_bad_good_example(self):
        self.assertIn("Build a Flask website using PostgreSQL, Redis, Docker", SYSTEM_PROMPT)
        self.assertIn("Do not introduce additional frameworks, databases, or infrastructure", SYSTEM_PROMPT)

    def test_contains_all_required_categories(self):
        for cat in self.REQUIRED_CATEGORIES:
            self.assertIn(cat, KNOWN_CATEGORIES)
        # Every category except "general" has dedicated construction guidance.
        for cat in self.REQUIRED_CATEGORIES - {"general"}:
            self.assertIn(f"### {cat}", SYSTEM_PROMPT, f"missing category guidance: {cat}")
        self.assertIn("- general", SYSTEM_PROMPT)

    def test_schema_has_requirement_separation_fields(self):
        for key in ("preserved_requirements", "assumptions", "missing_information", "suggestions"):
            self.assertIn(key, SYSTEM_PROMPT)

    def test_proportionality_rule_present(self):
        self.assertIn("Proportionality Rule", SYSTEM_PROMPT)


class ParseModelOutputTests(unittest.TestCase):
    def test_valid_raw_json(self):
        raw = (
            '{"detected_category": "coding", "detected_subcategory": "api", '
            '"detected_purpose": "Build a Flask API with login.", '
            '"persian_prompt": "پرامپت فارسی", "english_prompt": "Build a Flask API.", '
            '"preserved_requirements": ["Flask"], "assumptions": ["None"], '
            '"missing_information": ["Auth method"], "suggestions": ["Add tests"]}'
        )
        out = parse_model_output(raw)
        self.assertEqual(out["detected_category"], "coding")
        self.assertEqual(out["detected_subcategory"], "api")
        self.assertEqual(out["english_prompt"], "Build a Flask API.")
        self.assertEqual(out["persian_prompt"], "پرامپت فارسی")
        self.assertEqual(out["preserved_requirements"], ["Flask"])
        self.assertEqual(out["missing_information"], ["Auth method"])
        self.assertEqual(out["suggestions"], ["Add tests"])

    def test_markdown_wrapped_json(self):
        raw = "```json\n{\"detected_category\": \"research\", \"english_prompt\": \"Research X.\"}\n```"
        out = parse_model_output(raw)
        self.assertEqual(out["detected_category"], "research")
        self.assertEqual(out["english_prompt"], "Research X.")

    def test_invalid_json_falls_back_gracefully(self):
        out = parse_model_output("this is not json at all")
        self.assertEqual(out["detected_category"], "general")
        self.assertEqual(out["english_prompt"], "this is not json at all")
        self.assertEqual(out["preserved_requirements"], [])
        self.assertEqual(out["missing_information"], [])

    def test_unknown_category_normalized_to_general(self):
        raw = '{"detected_category": "something_unknown", "english_prompt": "X."}'
        out = parse_model_output(raw)
        self.assertEqual(out["detected_category"], "general")

    def test_empty_english_prompt_gets_placeholder(self):
        out = parse_model_output('{"detected_category": "general", "english_prompt": ""}')
        self.assertEqual(out["english_prompt"], "No prompt was generated.")

    def test_string_fields_normalized(self):
        raw = (
            '{"detected_category": "coding", "suggestions": "single string", '
            '"missing_information": "", "preserved_requirements": ["a", "  ", "b"]}'
        )
        out = parse_model_output(raw)
        self.assertEqual(out["suggestions"], ["single string"])
        self.assertEqual(out["missing_information"], [])
        self.assertEqual(out["preserved_requirements"], ["a", "b"])

    def test_each_category_is_accepted(self):
        for cat in KNOWN_CATEGORIES:
            out = parse_model_output(f'{{"detected_category": "{cat}", "english_prompt": "P."}}')
            self.assertEqual(out["detected_category"], cat)


class RepresentativePipelineTests(unittest.TestCase):
    """Simulate model output for the representative tasks and check the pipeline.

    Behavioral correctness against the live model is enforced by the system
    prompt (verified above); these tests verify the response pipeline survives
    realistic inputs for each scenario.
    """

    def test_simple_rewrite_task_stays_concise_shape(self):
        # "این متن رو رسمی‌تر کن." -> writing, short prompt, nothing invented.
        raw = (
            '{"detected_category": "writing", "detected_purpose": "Make the text more formal.", '
            '"english_prompt": "Rewrite this text in a more formal tone while preserving its meaning.", '
            '"persian_prompt": "این متن را با لحن رسمی‌تر بازنویسی کن.", '
            '"preserved_requirements": ["More formal tone"], '
            '"assumptions": [], "missing_information": [], "suggestions": []}'
        )
        out = parse_model_output(raw)
        self.assertEqual(out["detected_category"], "writing")
        self.assertLess(len(out["english_prompt"]), 200)
        self.assertEqual(out["preserved_requirements"], ["More formal tone"])

    def test_coding_task_no_invented_tech(self):
        # Flask + auth. The pipeline must NOT add PostgreSQL/JWT/Docker/React.
        raw = (
            '{"detected_category": "coding", "detected_subcategory": "api", '
            '"detected_purpose": "Build a Flask API with registration and login.", '
            '"english_prompt": "Build a Flask API where users can register and log in. '
            'Follow appropriate engineering practices compatible with the existing project. '
            'Do not introduce additional frameworks, databases, or infrastructure unless required or requested.", '
            '"persian_prompt": "یه API با Flask بساز که کاربران بتونن ثبت‌نام و لاگین کنن.", '
            '"preserved_requirements": ["Use Flask", "User registration", "Login"], '
            '"assumptions": [], "missing_information": ["Password storage method"], "suggestions": ["Add tests"]}'
        )
        out = parse_model_output(raw)
        eng = out["english_prompt"]
        self.assertEqual(out["detected_subcategory"], "api")
        self.assertIn("Flask", eng)
        for tech in ("PostgreSQL", "Redis", "Docker", "JWT", "React"):
            self.assertNotIn(tech, eng)
        self.assertIn("User registration", out["preserved_requirements"])

    def test_existing_technology_preserved(self):
        # "با Flask و PostgreSQL یه API برای سیستم کاریابی بساز." -> Flask + PostgreSQL MUST stay.
        raw = (
            '{"detected_category": "coding", "english_prompt": "Build a job-search system API '
            'using Flask and PostgreSQL.", "preserved_requirements": ["Use Flask", "Use PostgreSQL"], '
            '"missing_information": [], "assumptions": [], "suggestions": []}'
        )
        out = parse_model_output(raw)
        self.assertIn("Flask", out["english_prompt"])
        self.assertIn("PostgreSQL", out["english_prompt"])
        self.assertIn("Use PostgreSQL", out["preserved_requirements"])

    def test_ambiguous_request_reports_missing_information(self):
        # "یه سایت فروشگاهی برام بساز." -> must surface missing info, not pick a stack.
        raw = (
            '{"detected_category": "coding", "detected_subcategory": "web_development", '
            '"detected_purpose": "Build an e-commerce website.", '
            '"english_prompt": "Build an e-commerce website. Use the existing project\u2019s technology '
            'choices where applicable; do not introduce a stack on the user\u2019s behalf.", '
            '"preserved_requirements": ["E-commerce website"], '
            '"missing_information": ["Technology stack", "Payment gateway", "Product catalog needs"], '
            '"assumptions": ["A web application is implied"], "suggestions": []}'
        )
        out = parse_model_output(raw)
        self.assertGreaterEqual(len(out["missing_information"]), 3)
        self.assertNotIn("React", out["english_prompt"])

    def test_complex_multi_requirement_preserved(self):
        raw = (
            '{"detected_category": "coding", "english_prompt": "Build a job-search system with Flask '
            'and React that parses user resumes, supports employer profiles, and shows salary data.", '
            '"preserved_requirements": ["Flask", "React", "Resume parsing", "Employer profiles", '
            '"Salary display"], "assumptions": [], "missing_information": [], "suggestions": []}'
        )
        out = parse_model_output(raw)
        for req in ("Flask", "React", "Resume parsing", "Employer profiles", "Salary display"):
            self.assertIn(req, out["preserved_requirements"])

    def test_research_no_invented_citations(self):
        raw = (
            '{"detected_category": "research", "detected_subcategory": "literature_review", '
            '"english_prompt": "Write a study on the impact of AI on the job market over the next '
            '10 years using credible published articles.", '
            '"preserved_requirements": ["Impact of AI on job market", "Next 10 years"], '
            '"missing_information": ["Citation style"], "assumptions": [], "suggestions": []}'
        )
        out = parse_model_output(raw)
        self.assertEqual(out["detected_category"], "research")
        self.assertEqual(out["detected_subcategory"], "literature_review")
        self.assertIn("Citation style", out["missing_information"])


class FinalPolicyTests(unittest.TestCase):
    """Assert the final system-prompt rules (Persian preservation, interpretation
    boundary, missing-info/suggestions discipline, negative constraints, optional
    sections) are actually present."""

    def test_has_interpretation_boundary_section(self):
        self.assertIn("## Interpretation Boundary", SYSTEM_PROMPT)
        self.assertIn("Build a website similar to Divar", SYSTEM_PROMPT)
        self.assertIn("Do not automatically add authentication, search, categories, image upload, messaging, PostgreSQL, React, Flask", SYSTEM_PROMPT)

    def test_persian_prompt_is_translation_of_english(self):
        self.assertIn(
            "persian_prompt is produced ONLY from the finalized english_prompt",
            SYSTEM_PROMPT,
        )
        self.assertIn(
            "The original Persian user input is NOT an independent source for persian_prompt",
            SYSTEM_PROMPT,
        )
        self.assertIn(
            "single source of truth",
            SYSTEM_PROMPT,
        )

    def test_preserved_requirements_precise_rule(self):
        self.assertIn(
            "preserved_requirements must contain only requirements explicitly stated by the user "
            "or unambiguously implied by the request. Do not use this field for model "
            "recommendations, optional improvements, or arbitrary implementation choices.",
            SYSTEM_PROMPT,
        )

    def test_missing_information_filter_rule(self):
        self.assertIn(
            "Only report information as missing if its absence materially affects the ability "
            "to fulfill the user's request. Do not list optional details merely because they were not provided.",
            SYSTEM_PROMPT,
        )
        self.assertIn("Make this text more formal.", SYSTEM_PROMPT)
        self.assertIn("Do not report the target audience, exact formality level, word count, or formatting", SYSTEM_PROMPT)

    def test_suggestions_discipline_rule(self):
        self.assertIn(
            "Only provide suggestions when they provide meaningful value. "
            "For simple or sufficiently specified requests, return an empty suggestions array.",
            SYSTEM_PROMPT,
        )

    def test_negative_constraints_rule(self):
        self.assertIn(
            'Explicit exclusions, prohibitions, and "do not" instructions are hard constraints. '
            "They must be preserved in the generated prompt and must never be overridden by "
            "generic best practices or model preferences.",
            SYSTEM_PROMPT,
        )
        self.assertIn("you must never recommend anything that conflicts with a negative constraint", SYSTEM_PROMPT)

    def test_optional_sections_rule(self):
        self.assertIn(
            "Only include sections that contain useful information for the specific request. "
            "Do not create empty or artificial sections.",
            SYSTEM_PROMPT,
        )
        self.assertIn("force every prompt to use all sections", SYSTEM_PROMPT)


class FinalScenarioTests(unittest.TestCase):
    """Simulate compiler outputs for all ten representative inputs and verify the
    pipeline preserves the required semantics. Model behavior is steered by the
    system prompt (verified by FinalPolicyTests)."""

    def _parse(self, payload_dict):
        return parse_model_output(json.dumps(payload_dict, ensure_ascii=False))

    def test_01_simple_writing_request(self):
        # "این متن رو رسمی‌تر کن."
        out = self._parse({
            "detected_category": "writing",
            "detected_purpose": "Make the text more formal.",
            "english_prompt": "Rewrite this text in a more formal tone while preserving its meaning.",
            "persian_prompt": "این متن را با لحن رسمی‌تر بازنویسی کن.",
            "preserved_requirements": ["More formal tone"],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        self.assertEqual(out["detected_category"], "writing")
        self.assertLess(len(out["english_prompt"]), 150)
        self.assertEqual(out["missing_information"], [])
        self.assertEqual(out["suggestions"], [])
        # No invented audience/format/length/style requirements.
        for word in ("audience", "format", "word count", "tone of voice"):
            self.assertNotIn(word, out["english_prompt"].lower())

    def test_02_simple_translation_request(self):
        # "این متن رو انگلیسی کن."
        out = self._parse({
            "detected_category": "translation",
            "detected_purpose": "Translate the text into English.",
            "english_prompt": "Translate this text into English.",
            "persian_prompt": "این متن را انگلیسی کن.",
            "preserved_requirements": ["Translate to English"],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        self.assertEqual(out["detected_category"], "translation")
        self.assertLess(len(out["english_prompt"]), 100)
        self.assertEqual(out["suggestions"], [])
        for word in ("audience", "domain", "tone", "format"):
            self.assertNotIn(word, out["english_prompt"].lower())

    def test_03_flask_api_no_invented_stack(self):
        # "یه API با Flask بساز که کاربران بتونن ثبت‌نام و لاگین کنن."
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "api",
            "detected_purpose": "Build a Flask API with registration and login.",
            "english_prompt": "Build a Flask API where users can register and log in. "
                              "Follow appropriate engineering practices compatible with the existing project. "
                              "Do not introduce additional frameworks, databases, or infrastructure unless required or requested.",
            "persian_prompt": "یه API با Flask بساز که کاربران بتونن ثبت‌نام و لاگین کنن.",
            "preserved_requirements": ["Use Flask", "User registration", "Login"],
            "assumptions": [],
            "missing_information": ["Password storage method"],
            "suggestions": [],
        })
        self.assertIn("Flask", out["english_prompt"])
        for tech in ("PostgreSQL", "Redis", "Docker", "React", "JWT", "SQLAlchemy"):
            self.assertNotIn(tech, out["english_prompt"])
        self.assertIn("User registration", out["preserved_requirements"])

    def test_04_explicit_technology_constraints(self):
        # "با Flask و PostgreSQL یه API برای سیستم کاریابی بساز، ولی Docker استفاده نکن."
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "api",
            "detected_purpose": "Build a job-search system API with Flask and PostgreSQL, without Docker.",
            "english_prompt": "Build a job-search system API using Flask and PostgreSQL. "
                              "Do not use Docker.",
            "persian_prompt": "با Flask و PostgreSQL یه API برای سیستم کاریابی بساز؛ Docker استفاده نکن.",
            "preserved_requirements": [
                "Use Flask",
                "Use PostgreSQL",
                "Job-search system",
                "Do not use Docker",
            ],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        self.assertIn("Flask", out["english_prompt"])
        self.assertIn("PostgreSQL", out["english_prompt"])
        self.assertIn("job-search", out["english_prompt"])
        self.assertIn("Do not use Docker", out["english_prompt"])
        self.assertIn("Do not use Docker", out["preserved_requirements"])
        # Docker must not resurface as a recommendation.
        self.assertNotEqual(out["suggestions"], ["Add Docker"])
        self.assertNotIn("Docker", " ".join(out["suggestions"]))

    def test_05_ambiguous_website_request(self):
        # "یه سایت فروشگاهی برام بساز."
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "web_development",
            "detected_purpose": "Build an e-commerce website.",
            "english_prompt": "Build an e-commerce website. Use the existing project's technology "
                              "choices where applicable; do not introduce a stack on the user's behalf.",
            "persian_prompt": "یه سایت فروشگاهی برام بساز.",
            "preserved_requirements": ["E-commerce website"],
            "assumptions": ["A web application is implied"],
            "missing_information": ["Technology stack", "Payment gateway", "Product catalog needs"],
            "suggestions": [],
        })
        self.assertGreaterEqual(len(out["missing_information"]), 3)
        for tech in ("React", "Flask", "PostgreSQL", "Stripe", "Docker"):
            self.assertNotIn(tech, out["english_prompt"])

    def test_06_divar_like_request(self):
        # "یه سایت شبیه دیوار می‌خوام."
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "web_development",
            "detected_purpose": "Build a classified-ads website similar to Divar.",
            "english_prompt": "Build a classified-ads website similar to Divar. Preserve only the "
                              "behavior the user described; do not add features on the user's behalf.",
            "persian_prompt": "یه سایت شبیه دیوار می‌خوام.",
            "preserved_requirements": ["Classified-ads website", "Similar to Divar"],
            "assumptions": ["A web application is implied"],
            "missing_information": ["Which Divar features are required", "Technology stack"],
            "suggestions": [],
        })
        for feature in ("messaging", "authentication", "search", "image upload", "PostgreSQL", "React"):
            self.assertNotIn(feature, out["english_prompt"].lower())

    def test_07_complex_coding_request(self):
        # Multi-requirement coding request with an explicit exclusion.
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "web_development",
            "detected_purpose": "Build a task manager web app with a Python backend and SQLite database.",
            "english_prompt": "Build a task manager web application. Backend in Python. Use SQLite for storage. "
                              "Users can create, edit, delete, and mark tasks as done. Do not use a JavaScript frontend framework. "
                              "Follow appropriate engineering practices compatible with the existing project.",
            "persian_prompt": "یه اپ مدیریت کارها بساز؛ بک‌اند پایتون، دیتابیس SQLite، کاربران بتونن تسک بسازن، ویرایش کنن، حذف کنن و انجام‌شده علامت بزنن. فریم‌ورک فرانت‌اند جاوااسکریپت استفاده نکن.",
            "preserved_requirements": [
                "Task manager web app",
                "Python backend",
                "SQLite database",
                "Create/edit/delete tasks",
                "Mark tasks as done",
                "Do not use a JavaScript frontend framework",
            ],
            "assumptions": [],
            "missing_information": [],
            "suggestions": ["Add user authentication if required later"],
        })
        eng = out["english_prompt"]
        for phrase in ("task manager", "web application", "Python", "SQLite",
                       "create", "edit", "delete", "mark tasks as done"):
            self.assertIn(phrase, eng)
        self.assertIn("Do not use a JavaScript frontend framework", eng)
        self.assertNotIn("React", eng)
        self.assertNotIn("Redis", eng)
        self.assertIn("Do not use a JavaScript frontend framework", out["preserved_requirements"])

    def test_08_research_request(self):
        # Persian research request — no invented citation style/sources.
        out = self._parse({
            "detected_category": "research",
            "detected_subcategory": "literature_review",
            "detected_purpose": "Write a study on AI's impact on the job market over the next 10 years.",
            "english_prompt": "Write a study on the impact of artificial intelligence on the job market "
                              "over the next 10 years, based on credible published articles.",
            "persian_prompt": "مطالعه‌ای درباره تأثیر هوش مصنوعی بر بازار کار در ۱۰ سال آینده با استفاده از مقالات معتبر بنویس.",
            "preserved_requirements": ["Impact of AI on job market", "Next 10 years", "Use credible articles"],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        self.assertEqual(out["detected_category"], "research")
        for phrase in ("APA", "IEEE", "Scopus", "PubMed"):
            self.assertNotIn(phrase, out["english_prompt"])
        for req in ("Impact of AI on job market", "Next 10 years"):
            self.assertIn(req, out["preserved_requirements"])

    def test_09_suggestions_separation(self):
        # An optional improvement must live in suggestions only.
        out = self._parse({
            "detected_category": "research",
            "detected_purpose": "Summarize a dataset of user feedback.",
            "english_prompt": "Summarize the dataset of user feedback by topic and highlight the most common issues.",
            "persian_prompt": "دیتاست بازخورد کاربران را خلاصه کن و رایج‌ترین مشکلات را مشخص کن.",
            "preserved_requirements": ["Summarize user feedback", "Highlight common issues"],
            "assumptions": [],
            "missing_information": ["Dataset format"],
            "suggestions": ["Export a CSV chart of the most common issues"],
        })
        self.assertIn("Export a CSV chart of the most common issues", out["suggestions"])
        self.assertNotIn("CSV", out["english_prompt"])
        self.assertNotIn("CSV", " ".join(out["preserved_requirements"]))

    def test_10_proportionality(self):
        # Simple request -> short prompt; complex request -> structured prompt.
        simple = self._parse({
            "detected_category": "writing",
            "english_prompt": "Rewrite this text in a more formal tone.",
            "persian_prompt": "این متن را رسمی‌تر کن.",
            "preserved_requirements": ["More formal tone"],
            "missing_information": [],
            "suggestions": [],
        })["english_prompt"]
        complex_prompt = (
            "Build a job-search system with Flask and React that parses user resumes, "
            "supports employer profiles, and shows salary data. Requirements: "
            "Context: existing project. Task: implement the features above. "
            "Constraints: preserve current data model. Expected deliverables: working endpoints, "
            "tests for the parsing module."
        )
        complex_req = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "web_development",
            "english_prompt": complex_prompt,
            "persian_prompt": "سیستم کاریابی با Flask و React بساز که رزومه کاربران را تحلیل کند و پروفایل کارفرما و حقوق را نشان دهد.",
            "preserved_requirements": ["Flask", "React", "Resume parsing", "Employer profiles", "Salary display"],
            "missing_information": [],
            "assumptions": [],
            "suggestions": [],
        })["english_prompt"]
        self.assertLess(len(simple), 100)
        self.assertGreater(len(complex_req), len(simple) * 2)
        # No generic AI jargon inflated into the complex prompt.
        for phrase in ("cutting-edge", "leverage", "synergy", "state-of-the-art"):
            self.assertNotIn(phrase, complex_req.lower())


class EnglishPersianConsistencyTests(unittest.TestCase):
    """english_prompt is the canonical source and persian_prompt is its faithful
    Persian translation: same requirements, constraints, prohibitions, and scope."""

    def _parse(self, payload_dict):
        return parse_model_output(json.dumps(payload_dict, ensure_ascii=False))

    def test_prompt_enforces_canonical_source_flow(self):
        self.assertIn("compile(user_input) -> english_prompt", SYSTEM_PROMPT)
        self.assertIn("translate(english_prompt) -> persian_prompt", SYSTEM_PROMPT)
        self.assertIn("single source of truth", SYSTEM_PROMPT)
        self.assertNotIn("compile(user_input) -> persian_prompt", SYSTEM_PROMPT)

    def test_prompt_has_consistency_validation_step(self):
        self.assertIn("## Consistency Validation (English/Persian)", SYSTEM_PROMPT)
        self.assertIn("do NOT edit english_prompt to match persian_prompt", SYSTEM_PROMPT)
        self.assertIn("Regenerate persian_prompt from the finalized english_prompt", SYSTEM_PROMPT)

    def test_prompt_has_translation_fidelity_examples(self):
        self.assertIn("Do not use PostgreSQL.", SYSTEM_PROMPT)
        self.assertIn("از PostgreSQL استفاده نکن", SYSTEM_PROMPT)
        self.assertIn("Keep technical identifiers unchanged", SYSTEM_PROMPT)

    def test_01_simple_coding_request_english_and_persian_consistent(self):
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "api",
            "detected_purpose": "Build an API with Flask for managing users.",
            "english_prompt": "Build an API with Flask for managing users.",
            "persian_prompt": "یک API با Flask برای مدیریت کاربران بساز.",
            "preserved_requirements": ["Build an API", "Use Flask", "Manage users"],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        eng, per = out["english_prompt"], out["persian_prompt"]
        self.assertIn("Flask", eng)
        self.assertIn("Flask", per)
        self.assertIn("managing users", eng)
        self.assertIn("مدیریت کاربران", per)
        for tech in ("PostgreSQL", "Redis", "Docker", "JWT"):
            self.assertNotIn(tech, per)

    def test_02_multiple_technical_requirements_preserved(self):
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "api",
            "english_prompt": "Build an API with Flask and PostgreSQL for job search, "
                              "including user registration and login.",
            "persian_prompt": "یک API با Flask و PostgreSQL برای کاریابی بساز، "
                              "همراه با ثبت‌نام و ورود کاربران.",
            "preserved_requirements": ["Flask", "PostgreSQL", "Registration", "Login"],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        eng, per = out["english_prompt"], out["persian_prompt"]
        for ident in ("Flask", "PostgreSQL"):
            self.assertIn(ident, eng)
            self.assertIn(ident, per)
        self.assertIn("registration", eng)
        self.assertIn("login", eng)
        self.assertIn("ثبت‌نام", per)
        self.assertIn("ورود", per)
        for tech in ("Redis", "Docker", "JWT", "React"):
            self.assertNotIn(tech, per)

    def test_03_explicit_negative_constraint_preserved(self):
        # The example from the task: the PostgreSQL prohibition must survive at full
        # strength in Persian, and must never appear only in one version.
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "api",
            "english_prompt": "Build an API with Flask for managing users.\n\n"
                              "Constraint:\n* Do not use PostgreSQL.",
            "persian_prompt": "یک API با Flask برای مدیریت کاربران بساز.\n\n"
                              "محدودیت:\n* از PostgreSQL استفاده نکن.",
            "preserved_requirements": ["Build an API", "Use Flask", "Do not use PostgreSQL"],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        eng, per = out["english_prompt"], out["persian_prompt"]
        self.assertIn("Do not use PostgreSQL", eng)
        self.assertIn("از PostgreSQL استفاده نکن", per)
        self.assertNotIn("ترجیحاً", per)

    def test_04_multiple_features_consistent(self):
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "web_development",
            "english_prompt": "Build a task manager where users can create tasks, edit tasks, "
                              "delete tasks, and mark tasks as done.",
            "persian_prompt": "یک ابزار مدیریت کار بساز که کاربران می‌توانند کار بسازند، "
                              "ویرایش کنند، حذف کنند و انجام‌شده را علامت بزنند.",
            "preserved_requirements": ["Task manager", "Create", "Edit", "Delete", "Mark as done"],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        eng, per = out["english_prompt"], out["persian_prompt"]
        for feat in ("create", "edit", "delete", "mark tasks as done"):
            self.assertIn(feat, eng)
        for feat in ("بسازند", "ویرایش", "حذف", "انجام‌شده"):
            self.assertIn(feat, per)
        self.assertNotIn("PostgreSQL", per)

    def test_05_ambiguous_request_not_rewritten_differently(self):
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "web_development",
            "english_prompt": "Build an e-commerce website. Use the existing project's technology "
                              "choices where applicable; do not introduce a stack on the user's behalf.",
            "persian_prompt": "یک سایت فروشگاهی بساز. هر جا ممکن است از انتخاب‌های فنی "
                              "پروژه موجود استفاده کن؛ به جای کاربر استک فنی معرفی نکن.",
            "preserved_requirements": ["E-commerce website"],
            "assumptions": [],
            "missing_information": ["Technology stack", "Payment gateway"],
            "suggestions": [],
        })
        eng, per = out["english_prompt"], out["persian_prompt"]
        self.assertIn("e-commerce website", eng)
        self.assertIn("سایت فروشگاهی", per)
        self.assertIn("do not introduce a stack", eng)
        self.assertIn("استک فنی معرفی نکن", per)
        self.assertGreaterEqual(len(out["missing_information"]), 2)
        for tech in ("React", "Flask", "PostgreSQL", "Stripe", "Docker"):
            self.assertNotIn(tech, per)

    def test_06_technical_identifiers_unchanged(self):
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "web_development",
            "english_prompt": "Expose a REST API secured with JWT. Use SQLAlchemy as the ORM. "
                              "Write the frontend in TypeScript with React.",
            "persian_prompt": "یک REST API با امنیت JWT ارائه بده. از SQLAlchemy به عنوان ORM "
                              "استفاده کن. فرانت‌اند را با TypeScript و React بنویس.",
            "preserved_requirements": ["REST API", "JWT", "SQLAlchemy", "TypeScript", "React"],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        for ident in ("REST API", "JWT", "SQLAlchemy", "TypeScript", "React"):
            self.assertIn(ident, out["english_prompt"])
            self.assertIn(ident, out["persian_prompt"])

    def test_07_complex_multi_constraint_request(self):
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "web_development",
            "english_prompt": "Build a task manager web application. Backend in Python. "
                              "Use SQLite for storage. Users can create, edit, delete, and mark "
                              "tasks as done. Do not use a JavaScript frontend framework. "
                              "Do not use Docker.",
            "persian_prompt": "یک اپ وب مدیریت وظایف بساز. بک‌اند با Python. برای ذخیره‌سازی از "
                              "SQLite استفاده کن. کاربران می‌توانند وظایف را بسازند، ویرایش کنند، "
                              "حذف کنند و انجام‌شده علامت بزنند. از فریم‌ورک فرانت‌اند جاوااسکریپت "
                              "استفاده نکن. از Docker استفاده نکن.",
            "preserved_requirements": [
                "Task manager web app",
                "Python backend",
                "SQLite",
                "Do not use a JavaScript frontend framework",
                "Do not use Docker",
            ],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        eng, per = out["english_prompt"], out["persian_prompt"]
        for ident in ("Python", "SQLite", "Docker"):
            self.assertIn(ident, eng)
            self.assertIn(ident, per)
        for neg in ("Do not use a JavaScript frontend framework", "Do not use Docker"):
            self.assertIn(neg, eng)
        self.assertIn("استفاده نکن", per)
        self.assertNotIn("React", per)

    def test_08_structured_english_translated_with_structure(self):
        # The English prompt is significantly more structured than the loose Persian
        # input; the Persian must mirror that structure, not flatten the requirements.
        out = self._parse({
            "detected_category": "coding",
            "detected_subcategory": "api",
            "english_prompt": (
                "Context:\nAn existing project uses Python and Flask.\n\n"
                "Requirements:\n* Add user registration.\n* Add user login.\n\n"
                "Constraints:\n* Do not use PostgreSQL.\n\n"
                "Deliverables:\n* Working endpoints."
            ),
            "persian_prompt": (
                "زمینه:\nپروژه موجود از Python و Flask استفاده می‌کند.\n\n"
                "نیازمندی‌ها:\n* ثبت‌نام کاربران را اضافه کن.\n* ورود کاربران را اضافه کن.\n\n"
                "محدودیت‌ها:\n* از PostgreSQL استفاده نکن.\n\n"
                "تحویل‌شدنی‌ها:\n* اندپوینت‌های کارا."
            ),
            "preserved_requirements": ["User registration", "User login", "Do not use PostgreSQL"],
            "assumptions": [],
            "missing_information": [],
            "suggestions": [],
        })
        eng, per = out["english_prompt"], out["persian_prompt"]
        for section in ("Context", "Requirements", "Constraints", "Deliverables"):
            self.assertIn(section, eng)
        for section in ("زمینه", "نیازمندی‌ها", "محدودیت‌ها", "تحویل‌شدنی‌ها"):
            self.assertIn(section, per)
        self.assertIn("Do not use PostgreSQL", eng)
        self.assertIn("از PostgreSQL استفاده نکن", per)
        self.assertIn("Python", per)
        self.assertIn("Flask", per)


if __name__ == "__main__":
    unittest.main()
