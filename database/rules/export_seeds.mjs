/**
 * 导出规则 SQL 种子 — 与 backend/app/ziwei/rules/seed_generator.py 保持一致
 * 运行：node database/rules/export_seeds.mjs
 */
import { writeFileSync, mkdirSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = __dirname;
const DATA = join(OUT, "data");

const BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"];
const VERSION = "2026.07.22";

const NAYIN = {
  "甲子":["海中金","金",4],"乙丑":["海中金","金",4],"丙寅":["炉中火","火",6],"丁卯":["炉中火","火",6],
  "戊辰":["大林木","木",3],"己巳":["大林木","木",3],"庚午":["路旁土","土",5],"辛未":["路旁土","土",5],
  "壬申":["剑锋金","金",4],"癸酉":["剑锋金","金",4],"甲戌":["山头火","火",6],"乙亥":["山头火","火",6],
  "丙子":["涧下水","水",2],"丁丑":["涧下水","水",2],"戊寅":["城头土","土",5],"己卯":["城头土","土",5],
  "庚辰":["白蜡金","金",4],"辛巳":["白蜡金","金",4],"壬午":["杨柳木","木",3],"癸未":["杨柳木","木",3],
  "甲申":["泉中水","水",2],"乙酉":["泉中水","水",2],"丙戌":["屋上土","土",5],"丁亥":["屋上土","土",5],
  "戊子":["霹雳火","火",6],"己丑":["霹雳火","火",6],"庚寅":["松柏木","木",3],"辛卯":["松柏木","木",3],
  "壬辰":["长流水","水",2],"癸巳":["长流水","水",2],"甲午":["砂中金","金",4],"乙未":["砂中金","金",4],
  "丙申":["山下火","火",6],"丁酉":["山下火","火",6],"戊戌":["平地木","木",3],"己亥":["平地木","木",3],
  "庚子":["壁上土","土",5],"辛丑":["壁上土","土",5],"壬寅":["金箔金","金",4],"癸卯":["金箔金","金",4],
  "甲辰":["覆灯火","火",6],"乙巳":["覆灯火","火",6],"丙午":["天河水","水",2],"丁未":["天河水","水",2],
  "戊申":["大驿土","土",5],"己酉":["大驿土","土",5],"庚戌":["钗钏金","金",4],"辛亥":["钗钏金","金",4],
  "壬子":["桑柘木","木",3],"癸丑":["桑柘木","木",3],"甲寅":["大溪水","水",2],"乙卯":["大溪水","水",2],
  "丙辰":["沙中土","土",5],"丁巳":["沙中土","土",5],"戊午":["天上火","火",6],"己未":["天上火","火",6],
  "庚申":["石榴木","木",3],"辛酉":["石榴木","木",3],"壬戌":["大海水","水",2],"癸亥":["大海水","水",2],
};

const FOUR = {
  "甲":{lu:"廉贞",quan:"破军",ke:"武曲",ji:"太阳"},"乙":{lu:"天机",quan:"天梁",ke:"紫微",ji:"太阴"},
  "丙":{lu:"天同",quan:"天机",ke:"文昌",ji:"廉贞"},"丁":{lu:"太阴",quan:"天同",ke:"天机",ji:"巨门"},
  "戊":{lu:"贪狼",quan:"太阴",ke:"右弼",ji:"天机"},"己":{lu:"武曲",quan:"贪狼",ke:"天梁",ji:"文曲"},
  "庚":{lu:"太阳",quan:"武曲",ke:"太阴",ji:"天同"},"辛":{lu:"巨门",quan:"太阳",ke:"文曲",ji:"文昌"},
  "壬":{lu:"天梁",quan:"紫微",ke:"左辅",ji:"武曲"},"癸":{lu:"破军",quan:"巨门",ke:"太阴",ji:"贪狼"},
};

const BRIGHTNESS = {
  "紫微":{"子":"平","丑":"庙","寅":"庙","卯":"旺","辰":"得","巳":"旺","午":"庙","未":"庙","申":"旺","酉":"旺","戌":"得","亥":"旺"},
  "天机":{"子":"庙","丑":"陷","寅":"得","卯":"旺","辰":"利","巳":"平","午":"庙","未":"陷","申":"得","酉":"旺","戌":"利","亥":"平"},
  "太阳":{"子":"陷","丑":"不得","寅":"旺","卯":"庙","辰":"旺","巳":"旺","午":"旺","未":"得","申":"得","酉":"平","戌":"不得","亥":"陷"},
  "武曲":{"子":"旺","丑":"庙","寅":"得","卯":"利","辰":"庙","巳":"平","午":"旺","未":"庙","申":"得","酉":"利","戌":"庙","亥":"平"},
  "天同":{"子":"旺","丑":"不得","寅":"利","卯":"平","辰":"平","巳":"庙","午":"陷","未":"不得","申":"旺","酉":"平","戌":"平","亥":"庙"},
  "廉贞":{"子":"平","丑":"利","寅":"庙","卯":"平","辰":"利","巳":"平","午":"庙","未":"利","申":"庙","酉":"平","戌":"利","亥":"平"},
  "天府":{"子":"庙","丑":"庙","寅":"庙","卯":"得","辰":"庙","巳":"得","午":"旺","未":"庙","申":"得","酉":"旺","戌":"庙","亥":"得"},
  "太阴":{"子":"庙","丑":"庙","寅":"陷","卯":"陷","辰":"陷","巳":"陷","午":"陷","未":"陷","申":"得","酉":"旺","戌":"旺","亥":"庙"},
  "贪狼":{"子":"旺","丑":"庙","寅":"平","卯":"利","辰":"庙","巳":"平","午":"旺","未":"庙","申":"平","酉":"利","戌":"庙","亥":"平"},
  "巨门":{"子":"旺","丑":"不得","寅":"庙","卯":"庙","辰":"陷","巳":"旺","午":"旺","未":"不得","申":"庙","酉":"庙","戌":"陷","亥":"旺"},
  "天相":{"子":"庙","丑":"庙","寅":"庙","卯":"陷","辰":"得","巳":"得","午":"庙","未":"得","申":"庙","酉":"陷","戌":"得","亥":"得"},
  "天梁":{"子":"庙","丑":"旺","寅":"庙","卯":"庙","辰":"庙","巳":"陷","午":"庙","未":"旺","申":"陷","酉":"得","戌":"庙","亥":"陷"},
  "七杀":{"子":"旺","丑":"庙","寅":"庙","卯":"旺","辰":"庙","巳":"平","午":"旺","未":"庙","申":"庙","酉":"旺","戌":"庙","亥":"平"},
  "破军":{"子":"庙","丑":"旺","寅":"得","卯":"陷","辰":"旺","巳":"平","午":"庙","未":"旺","申":"得","酉":"陷","戌":"旺","亥":"平"},
};

function calcZiwei(day, bureau) {
  const remainder = day % bureau;
  let quotient = Math.floor(day / bureau);
  if (remainder !== 0) quotient += 1;
  let index = quotient - 1;
  if (remainder !== 0) index -= 1;
  return BRANCHES[(2 + index) % 12];
}

function sq(v) { return `'${String(v).replace(/'/g, "''")}'`; }
function jq(v) { return sq(JSON.stringify(v)); }

mkdirSync(DATA, { recursive: true });

// nayin
let sql = ["-- nayin_rules", "DELETE FROM public.nayin_rules WHERE school = 'sanhe';", ""];
for (const [gz, [nayin, el, num]] of Object.entries(NAYIN)) {
  sql.push(`INSERT INTO public.nayin_rules (heavenly_stem, earthly_branch, nayin, element, bureau_number, school, version) VALUES (${sq(gz[0])}, ${sq(gz[1])}, ${sq(nayin)}, ${sq(el)}, ${num}, 'sanhe', '${VERSION}');`);
}
writeFileSync(join(OUT, "nayin_rules.sql"), sql.join("\n"), "utf8");

// four transform
sql = ["-- four_transform_rules", "DELETE FROM public.four_transform_rules WHERE school = 'sanhe';", ""];
for (const [stem, t] of Object.entries(FOUR)) {
  sql.push(`INSERT INTO public.four_transform_rules (heavenly_stem, lu_star, quan_star, ke_star, ji_star, school, version) VALUES (${sq(stem)}, ${sq(t.lu)}, ${sq(t.quan)}, ${sq(t.ke)}, ${sq(t.ji)}, 'sanhe', '${VERSION}');`);
}
writeFileSync(join(OUT, "four_transform_rules.sql"), sql.join("\n"), "utf8");

// daxian
sql = ["-- daxian_rules", "DELETE FROM public.daxian_rules WHERE school = 'sanhe';", ""];
for (const r of [
  ["male","yang","forward"],["male","yin","backward"],["female","yang","backward"],["female","yin","forward"]
]) {
  sql.push(`INSERT INTO public.daxian_rules (gender, year_yinyang, direction, start_age_formula, school, version) VALUES (${sq(r[0])}, ${sq(r[1])}, ${sq(r[2])}, 'bureau_number', 'sanhe', '${VERSION}');`);
}
writeFileSync(join(OUT, "daxian_rules.sql"), sql.join("\n"), "utf8");

// ziwei position
sql = ["-- ziwei_position_rules", "DELETE FROM public.ziwei_position_rules WHERE school = 'sanhe';", ""];
for (const bureau of [2,3,4,5,6]) {
  for (let day = 1; day <= 30; day++) {
    sql.push(`INSERT INTO public.ziwei_position_rules (bureau, lunar_day, ziwei_branch, school, version) VALUES (${bureau}, ${day}, ${sq(calcZiwei(day, bureau))}, 'sanhe', '${VERSION}');`);
  }
}
writeFileSync(join(OUT, "ziwei_position_rules.sql"), sql.join("\n"), "utf8");

// brightness
sql = ["-- brightness_rules", "DELETE FROM public.brightness_rules WHERE school = 'sanhe';", ""];
for (const [star, branches] of Object.entries(BRIGHTNESS)) {
  for (const [branch, b] of Object.entries(branches)) {
    sql.push(`INSERT INTO public.brightness_rules (star_name, branch, brightness, school, version) VALUES (${sq(star)}, ${sq(branch)}, ${sq(b)}, 'sanhe', '${VERSION}');`);
  }
}
writeFileSync(join(OUT, "brightness_rules.sql"), sql.join("\n"), "utf8");

// star_placement (main stars)
const MAIN_PLACEMENT = [
  ["紫微","self","forward",0],["天机","紫微","backward",1],["太阳","紫微","backward",3],
  ["武曲","紫微","backward",4],["天同","紫微","backward",5],["廉贞","紫微","backward",8],
  ["天府","紫微","opposite",0],["太阴","天府","forward",1],["贪狼","天府","forward",2],
  ["巨门","天府","forward",3],["天相","天府","forward",4],["天梁","天府","forward",5],
  ["七杀","天府","forward",6],["破军","天府","forward",10],
];
sql = ["-- star_placement_rules", "DELETE FROM public.star_placement_rules WHERE school = 'sanhe';", ""];
for (const [star, base, dir, off] of MAIN_PLACEMENT) {
  sql.push(`INSERT INTO public.star_placement_rules (rule_type, star_name, base_star, direction, offset, condition, school, version) VALUES ('main_star', ${sq(star)}, ${sq(base)}, ${sq(dir)}, ${off}, '{}', 'sanhe', '${VERSION}');`);
}
const AUX = [
  ["左辅","aux_star","lunar_month"],["右弼","aux_star","lunar_month"],["文昌","aux_star","hour_branch"],
  ["文曲","aux_star","hour_branch"],["天魁","aux_star","year_stem"],["天钺","aux_star","year_stem"],
  ["禄存","aux_star","year_stem"],["擎羊","sha_star","year_stem"],["陀罗","sha_star","year_stem"],
  ["火星","sha_star","year_branch_hour"],["铃星","sha_star","year_branch_hour"],
  ["地空","sha_star","hour_branch"],["地劫","sha_star","hour_branch"],["天马","za_star","year_branch"],
];
for (const [star, type, by] of AUX) {
  sql.push(`INSERT INTO public.star_placement_rules (rule_type, star_name, base_star, direction, offset, condition, school, version) VALUES (${sq(type)}, ${sq(star)}, '', 'lookup', 0, ${jq({by})}, 'sanhe', '${VERSION}');`);
}
writeFileSync(join(OUT, "star_placement_rules.sql"), sql.join("\n"), "utf8");

// combinations (20)
const COMBOS = [
  ["紫府同宫",["紫微","天府"],"main_combo","管理能力,资源整合,领导型人格"],
  ["杀破狼",["七杀","破军","贪狼"],"main_combo","开创变革,大起大落,行动力强"],
  ["机月同梁",["天机","太阴","天同","天梁"],"main_combo","智慧型,服务导向,稳定发展"],
  ["日月并明",["太阳","太阴"],"main_combo","光明磊落,贵气十足,公众形象佳"],
  ["昌曲同宫",["文昌","文曲"],"aux_combo","才华横溢,文笔出众,学术优势"],
  ["魁钺夹命",["天魁","天钺"],"aux_combo","贵人相助,机遇较多,逢凶化吉"],
  ["禄马交驰",["禄存","天马"],"aux_combo","动中求财,事业奔波,财富流动"],
  ["火铃同宫",["火星","铃星"],"aux_combo","性格急躁,突发变动,需注意情绪"],
  ["羊陀夹命",["擎羊","陀罗"],"aux_combo","波折较多,需防刑伤,坚韧考验"],
  ["紫微独坐",["紫微"],"main_combo","独立领导,自我要求高,权威气质"],
  ["廉贞七杀",["廉贞","七杀"],"main_combo","权力欲望,竞争意识,事业冲劲"],
  ["武曲贪狼",["武曲","贪狼"],"main_combo","财富追求,社交能力,多元发展"],
  ["天同太阴",["天同","太阴"],"main_combo","温和内敛,感情细腻,享受生活"],
  ["太阳化禄",["太阳"],"sihua_combo","事业机遇,名声提升,贵人提拔"],
  ["太阴化科",["太阴"],"sihua_combo","名声远播,才学显现,温和贵人"],
  ["武曲化权",["武曲"],"sihua_combo","掌财能力,执行力强,事业主导"],
  ["天同化忌",["天同"],"sihua_combo","情绪困扰,福德有损,需调节心态"],
  ["廉贞化禄",["廉贞"],"sihua_combo","桃花财禄,人际活跃,创意变现"],
  ["破军化权",["破军"],"sihua_combo","破旧立新,变革领导,突破困境"],
  ["紫府朝垣",["紫微","天府"],"main_combo","格局清贵,事业稳定,管理天赋"],
];
sql = ["-- star_combination_rules", "DELETE FROM public.star_combination_rules WHERE school = 'sanhe';", ""];
for (const [name, stars, cat, tags] of COMBOS) {
  const t = tags.split(",");
  sql.push(`INSERT INTO public.star_combination_rules (combination_name, stars, category, personality, career, wealth, relationship, ai_prompt, school, version) VALUES (${sq(name)}, ${jq(stars)}, ${sq(cat)}, ${sq(t[0]||"")}, ${sq(t[1]||"")}, ${sq(t[2]||"")}, '', ${sq(`分析${name}组合`)}, 'sanhe', '${VERSION}');`);
}
writeFileSync(join(OUT, "star_combination_rules.sql"), sql.join("\n"), "utf8");

// palace meanings
const PALACES = [
  ["命宫","自我","代表先天性格、人生格局与整体运势"],
  ["兄弟","手足","代表兄弟姐妹、同事及平辈关系"],
  ["夫妻","配偶","代表婚姻感情、配偶特质与恋爱模式"],
  ["子女","后代","代表子女缘分、创造力与投资"],
  ["财帛","财富","代表赚钱能力、理财模式与物质资源"],
  ["疾厄","健康","代表身体健康、灾厄与内在情绪"],
  ["迁移","外出","代表外出运、社会形象与外界评价"],
  ["交友","人际","代表朋友、下属与人际网络"],
  ["官禄","事业","代表事业发展、工作成就与社会地位"],
  ["田宅","不动产","代表家庭环境、房产与内在安全感"],
  ["福德","精神","代表精神世界、享受能力与福报"],
  ["父母","长辈","代表父母缘分、上司关系与遗传背景"],
];
sql = ["-- palace_meaning_rules", "DELETE FROM public.palace_meaning_rules WHERE school = 'sanhe';", ""];
for (const [name, kw, meaning] of PALACES) {
  sql.push(`INSERT INTO public.palace_meaning_rules (palace_name, keyword, meaning, career, wealth, relationship, health, ai_prompt, school, version) VALUES (${sq(name)}, ${sq(kw)}, ${sq(meaning)}, '', '', '', '', ${sq(`解读${name}：${meaning}`)}, 'sanhe', '${VERSION}');`);
}
writeFileSync(join(OUT, "palace_meaning_rules.sql"), sql.join("\n"), "utf8");

// stars metadata (main + key aux)
const STARS = [
  ["紫微","土","阴","main",["领导","权威"]],["天机","木","阴","main",["智慧","谋略"]],
  ["太阳","火","阳","main",["光明","贵气"]],["武曲","金","阴","main",["财富","刚毅"]],
  ["天同","水","阳","main",["福德","温和"]],["廉贞","火","阴","main",["政治","桃花"]],
  ["天府","土","阳","main",["库藏","管理"]],["太阴","水","阴","main",["财富","母性"]],
  ["贪狼","木","阳","main",["欲望","桃花"]],["巨门","水","阴","main",["口才","暗蔽"]],
  ["天相","水","阳","main",["印信","辅助"]],["天梁","土","阳","main",["荫庇","清高"]],
  ["七杀","金","阳","main",["将星","冲动"]],["破军","水","阴","main",["破坏","开创"]],
  ["左辅","土","阳","aux",["辅助"]],["右弼","水","阴","aux",["辅助"]],
  ["文昌","金","阳","aux",["文才"]],["文曲","水","阴","aux",["文才"]],
  ["天魁","火","阳","aux",["贵人"]],["天钺","火","阴","aux",["贵人"]],
  ["禄存","土","阴","aux",["财禄"]],["天马","火","阳","za",["变动"]],
  ["擎羊","金","阳","sha",["刑伤"]],["陀罗","金","阴","sha",["拖延"]],
  ["火星","火","阳","sha",["爆发"]],["铃星","火","阴","sha",["焦虑"]],
  ["地空","火","阴","sha",["空亡"]],["地劫","火","阳","sha",["破耗"]],
];
sql = ["-- stars 星曜元数据", "DELETE FROM public.stars WHERE school = 'sanhe';", ""];
for (const [name, el, yy, cat, kw] of STARS) {
  sql.push(`INSERT INTO public.stars (name, element, yin_yang, category, keywords, personality_tags, career_tags, wealth_tags, relationship_tags, description, ai_prompt, school, is_active) VALUES (${sq(name)}, ${sq(el)}, ${sq(yy)}, ${sq(cat)}, ${jq(kw)}, ${jq(kw)}, ${jq(kw.slice(0,2))}, ${jq(kw.slice(0,1))}, ${jq(kw.slice(0,1))}, ${sq(`${name}星`)}, ${sq(`解读${name}`)}, 'sanhe', true);`);
}
writeFileSync(join(OUT, "stars.sql"), sql.join("\n"), "utf8");

console.log("Exported all rule seeds to", OUT);
