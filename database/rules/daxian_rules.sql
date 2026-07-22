-- daxian_rules
DELETE FROM public.daxian_rules WHERE school = 'sanhe';

INSERT INTO public.daxian_rules (gender, year_yinyang, direction, start_age_formula, school, version) VALUES ('male', 'yang', 'forward', 'bureau_number', 'sanhe', '2026.07.22');
INSERT INTO public.daxian_rules (gender, year_yinyang, direction, start_age_formula, school, version) VALUES ('male', 'yin', 'backward', 'bureau_number', 'sanhe', '2026.07.22');
INSERT INTO public.daxian_rules (gender, year_yinyang, direction, start_age_formula, school, version) VALUES ('female', 'yang', 'backward', 'bureau_number', 'sanhe', '2026.07.22');
INSERT INTO public.daxian_rules (gender, year_yinyang, direction, start_age_formula, school, version) VALUES ('female', 'yin', 'forward', 'bureau_number', 'sanhe', '2026.07.22');