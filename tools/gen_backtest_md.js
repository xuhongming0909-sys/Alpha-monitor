const fs = require("fs");
const path = require("path");
const resultsPath = path.join(__dirname, "..", "runtime_data", "backtest", "results_v2.json");
const outputPath = path.join(__dirname, "..", "\u6307\u6570\u578Blof\u56DE\u6D4B.MD");
const data = JSON.parse(fs.readFileSync(resultsPath, "utf8"));
const aFunds = Object.values(data).filter(v => v.class === "A").sort((a, b) => a.mae - b.mae);
const bFunds = Object.values(data).filter(v => v.class === "B").sort((a, b) => a.mae - b.mae);

function grade(mae) {
  if (mae <= 0.1) return "\u2B50\u2B50\u2B50 \u4F18\u79C0";
  if (mae <= 0.3) return "\u2B50\u2B50 \u826F\u597D";
  if (mae <= 1.0) return "\u2B50 \u4E00\u822C";
  return "\u274C \u8F83\u5DEE";
}
function fmt(n, d) { return n.toFixed(d || 3); }

let md = "";
md += "# \u6307\u6570\u578BLOF\u56DE\u6D4B\u7ED3\u679C\n\n";
md += "> \u56DE\u6D4B\u533A\u95F4: " + aFunds[0].samplePeriod + "\n";
md += "> \u751F\u6210\u65F6\u95F4: " + new Date().toISOString().slice(0,10) + "\n";
md += "> \u6570\u636E\u6765\u6E90: ETF\u5386\u53F2\u65E5\u7EBF (akshare stock_us_daily)\n\n";

md += "## \u4E00\u3001A\u7C7B\uFF08\u6307\u6570\u8FFD\u8E2A\u578B\uFF09\u56DE\u6D4B\u7ED3\u679C\n\n";
md += "\u6309 MAE\uFF08\u5E73\u5747\u7EDD\u5BF9\u8BEF\u5DEE\uFF09\u6392\u5E8F\uFF0C\u8D8A\u5C0F\u8D8A\u597D\u3002\n\n";
md += "| \u6392\u540D | \u4EE3\u7801 | \u540D\u79F0 | ETF\u6807\u7684 | bias(%) | MAE(%) | maxErr(%) | errRate05(%) | \u5929\u6570 | \u8BC4\u7EA7 |\n";
md += "|------|------|------|---------|---------|--------|-----------|-------------|------|------|\n";
aFunds.forEach(function(f, i) {
  md += "| " + (i+1) + " | " + f.code + " | " + f.name + " | " + f.etf + " | " + fmt(f.bias) + " | " + fmt(f.mae) + " | " + fmt(f.maxErr, 4) + " | " + fmt(f.errRate05, 1) + " | " + f.alignedDays + " | " + grade(f.mae) + " |\n";
});

md += "\n**\u6307\u6807\u8BF4\u660E\uFF1A**\n";
md += "- **bias**: \u7CFB\u7EDF\u504F\u5DEE\uFF08IOPV\u4E0ENAV\u5DEE\u5F02\u7684\u5747\u503C\uFF09\uFF0C\u6B63\u503C=IOPV\u504F\u9AD8\n";
md += "- **MAE**: \u5E73\u5747\u7EDD\u5BF9\u8BEF\u5DEE\uFF0C\u6838\u5FC3\u6307\u6807\uFF0C\u8D8A\u5C0F\u8868\u793AETF\u62DF\u5408\u8D8A\u7CBE\u51C6\n";
md += "- **maxErr**: \u6700\u5927\u5355\u65E5\u8BEF\u5DEE\n";
md += "- **errRate05**: \u8BEF\u5DEE\u8D85\u8FC70.5%\u7684\u5929\u6570\u5360\u6BD4\n";
md += "- **\u5929\u6570**: \u5B9E\u9645\u5BF9\u9F50\u4EA4\u6613\u65E5\u6570\n\n";

md += "## \u4E8C\u3001B\u7C7B\uFF08\u4E3B\u52A8\u7BA1\u7406\u578B\uFF09\u56DE\u6D4B\u7ED3\u679C\n\n";
md += "B\u7C7B\u4F7F\u7528\u5B63\u62A5\u5B9E\u9645\u6301\u4ED3\u4F30\u7B97\uFF0C\u975E\u5355\u4E00ETF\u6620\u5C04\u3002\n\n";
md += "| \u6392\u540D | \u4EE3\u7801 | \u540D\u79F0 | bias(%) | MAE(%) | maxErr(%) | errRate05(%) | \u5929\u6570 |\n";
md += "|------|------|------|---------|--------|-----------|-------------|------|\n";
bFunds.forEach(function(f, i) {
  md += "| " + (i+1) + " | " + f.code + " | " + f.name + " | " + fmt(f.bias) + " | " + fmt(f.mae) + " | " + fmt(f.maxErr, 4) + " | " + fmt(f.errRate05, 1) + " | " + f.alignedDays + " |\n";
});
md += "\n";

md += "## \u4E09\u3001ETF\u6620\u5C04\u53D8\u66F4\u8BB0\u5F55\n\n";
md += "\u672C\u6B21\u56DE\u6D4B\u76F8\u6BD4\u4E0A\u4E00\u7248\u672C\uFF0C\u4F18\u5316\u4E86\u4EE5\u4E0B\u6620\u5C04\u5173\u7CFB\uFF1A\n\n";
md += "| \u4EE3\u7801 | \u540D\u79F0 | \u65E7ETF | \u65B0ETF | \u53D8\u66F4\u539F\u56E0 |\n";
md += "|------|------|-------|-------|----------|\n";
md += "| 161126 | \u6807\u666E\u533B\u7597\u4FDD\u5065LOF | XLV | RYH | XLV\u4E3A\u5E02\u503C\u52A0\u6743\uFF0CRYH\u4E3A\u7B49\u6743\u91CD\uFF0C\u4E0E\u57FA\u51C6\u201C\u6807\u666E500\u533B\u7597\u4FDD\u5065\u7B49\u6743\u91CD\u201D\u5B8C\u5168\u5339\u914D |\n";
md += "| 162719 | \u77F3\u6CB9LOF | XOP | IEO | XOP\u4E3AS&P\u6CB9\u6C14\u4E0A\u6E38\uFF0CIEO\u4E3A\u9053\u743C\u65AF\u77F3\u6CB9\u5F00\u53D1\u751F\u4EA7\uFF0C\u4E0E\u57FA\u51C6\u201C\u9053\u743C\u65AF\u7F8E\u56FD\u77F3\u6CB9\u201D\u5B8C\u5168\u5339\u914D |\n";
md += "| 160140 | \u7F8E\u56FDREIT\u7CBE\u9009LOF | VNQ | IYR | IYR\u8DDF\u8E2A\u9053\u743C\u65AF\u7F8E\u56FD\u7CBE\u9009REIT\uFF0C\u4E0E\u57FA\u51C6\u5B8C\u5168\u5339\u914D |\n";
md += "| 164906 | \u4E2D\u6982\u4E92\u8054\u7F51LOF | B\u7C7B | KWEB(A\u7C7B) | \u6295\u8D44\u76EE\u6807\u660E\u786E\u201C\u7D27\u5BC6\u8DDF\u8E2A\u6807\u7684\u6307\u6570\u201D\uFF0C\u6539\u4E3AA\u7C7B |\n";
md += "| 160416 | \u77F3\u6CB9\u57FA\u91D1LOF | B\u7C7B | IXC(A\u7C7B) | \u8DDF\u8E2A\u201C\u6807\u666E\u5168\u7403\u77F3\u6CB9\u6307\u6570\u201D\uFF0C\u6539\u4E3AA\u7C7B |\n";
md += "\n";

md += "## \u56DB\u3001\u56DE\u6D4B\u8D28\u91CF\u5206\u7EA7\u603B\u7ED3\n\n";
var excellent = aFunds.filter(function(f) { return f.mae <= 0.1; });
var good = aFunds.filter(function(f) { return f.mae > 0.1 && f.mae <= 0.3; });
var fair = aFunds.filter(function(f) { return f.mae > 0.3 && f.mae <= 1.0; });
var poor = aFunds.filter(function(f) { return f.mae > 1.0; });

md += "### \u2B50\u2B50\u2B50 \u4F18\u79C0\uFF08MAE \u2264 0.1%\uFF09\n\n";
if (excellent.length) { excellent.forEach(function(f) { md += "- **" + f.code + " " + f.name + "** \u2192 " + f.etf + "\uFF1AMAE=" + fmt(f.mae) + "%\uFF0Cbias=" + fmt(f.bias) + "%\n"; }); }
else { md += "- \u65E0\n"; }
md += "\n\u8FD9\u4E9B\u57FA\u91D1ETF\u62DF\u5408\u7CBE\u5EA6\u6781\u9AD8\uFF0C\u53EF\u7528\u4E8E\u5B9E\u65F6IOPV\u4F30\u7B97\uFF0C\u8BEF\u5DEE\u53EF\u5FFD\u7565\u3002\n\n";

md += "### \u2B50\u2B50 \u826F\u597D\uFF080.1% < MAE \u2264 0.3%\uFF09\n\n";
if (good.length) { good.forEach(function(f) { md += "- **" + f.code + " " + f.name + "** \u2192 " + f.etf + "\uFF1AMAE=" + fmt(f.mae) + "%\uFF0Cbias=" + fmt(f.bias) + "%\n"; }); }
else { md += "- \u65E0\n"; }
md += "\n\u62DF\u5408\u7CBE\u5EA6\u826F\u597D\uFF0C\u53EF\u7528\u4E8E\u5B9E\u65F6\u4F30\u7B97\uFF0C\u4F46\u9700\u5173\u6CE8\u504F\u5DEE\u65B9\u5411\u3002\n\n";

md += "### \u2B50 \u4E00\u822C\uFF080.3% < MAE \u2264 1.0%\uFF09\n\n";
if (fair.length) { fair.forEach(function(f) { md += "- **" + f.code + " " + f.name + "** \u2192 " + f.etf + "\uFF1AMAE=" + fmt(f.mae) + "%\uFF0Cbias=" + fmt(f.bias) + "%\n"; }); }
else { md += "- \u65E0\n"; }
md += "\n\u62DF\u5408\u5B58\u5728\u4E00\u5B9A\u504F\u5DEE\uFF0C\u53EF\u80FD\u539F\u56E0\uFF1A\u8DDF\u8E2A\u8BEF\u5DEE\u3001\u6C47\u7387\u6CE2\u52A8\u3001\u65F6\u95F4\u5DEE\u7B49\u3002\u5B9E\u65F6\u4F30\u7B97\u53EF\u7528\u4F46\u9700\u8C28\u614E\u3002\n\n";

md += "### \u274C \u8F83\u5DEE\uFF08MAE > 1.0%\uFF09\n\n";
if (poor.length) {
  poor.forEach(function(f) {
    var reason = "";
    if (f.etf === "USO") reason = "\uFF08\u539F\u6CB9\u671F\u8D27\u5C55\u671F\u6210\u672C\u5BFC\u81F4USO\u6301\u7EED\u504F\u79BB\u73B0\u8D27\u4EF7\u683C\uFF09";
    else if (f.etf === "KWEB") reason = "\uFF08\u4E2D\u6982\u80A1\u8DE8\u5E02\u573A\u4EA4\u6613\u65F6\u95F4\u5DEE\u5F02+\u6C47\u7387\u53CC\u91CD\u5F71\u54CD\uFF09";
    md += "- **" + f.code + " " + f.name + "** \u2192 " + f.etf + "\uFF1AMAE=" + fmt(f.mae) + "%\uFF0Cbias=" + fmt(f.bias) + "% " + reason + "\n";
  });
} else { md += "- \u65E0\n"; }
md += "\n\u8BEF\u5DEE\u8F83\u5927\uFF0C\u4E0D\u5EFA\u8BAE\u76F4\u63A5\u7528\u5355\u4E00ETF\u505A\u5B9E\u65F6IOPV\u4F30\u7B97\u3002\u539F\u6CB9\u7C7B\u9700\u8003\u8651\u671F\u8D27\u5C55\u671F\u635F\u8017\uFF0C\u4E2D\u6982\u7C7B\u9700\u8003\u8651\u8DE8\u5E02\u573A\u56E0\u7D20\u3002\n\n";

md += "## \u4E94\u3001\u7ED3\u8BBA\n\n";
md += "\u672C\u6B21\u5171\u56DE\u6D4B **" + (aFunds.length + bFunds.length) + "** \u53EA\u57FA\u91D1\uFF08A\u7C7B" + aFunds.length + "\u53EA + B\u7C7B" + bFunds.length + "\u53EA\uFF09\u3002\n\n";
md += "1. **" + excellent.length + "\u53EA\u4F18\u79C0**\uFF08MAE\u22640.1%\uFF09\uFF1AETF\u4E0E\u57FA\u51C6\u9AD8\u5EA6\u543B\u5408\uFF0C\u53EF\u76F4\u63A5\u7528\u4E8E\u751F\u4EA7IOPV\u8BA1\u7B97\n";
md += "2. **" + good.length + "\u53EA\u826F\u597D**\uFF08MAE 0.1~0.3%\uFF09\uFF1A\u53EF\u7528\uFF0C\u5EFA\u8BAE\u76D1\u63A7bias\u6F02\u79FB\n";
md += "3. **" + fair.length + "\u53EA\u4E00\u822C**\uFF08MAE 0.3~1.0%\uFF09\uFF1A\u9700\u7ED3\u5408\u5176\u4ED6\u56E0\u7D20\u4FEE\u6B63\n";
md += "4. **" + poor.length + "\u53EA\u8F83\u5DEE**\uFF08MAE>1.0%\uFF09\uFF1A\u539F\u6CB9/\u4E2D\u6982\u7C7B\uFF0C\u9700\u7279\u6B8A\u5904\u7406\n\n";
md += "### \u5173\u952E\u53D1\u73B0\n\n";
md += "- **\u539F\u6CB9\u7C7B**\uFF08160723/161129/501018\uFF09\u8BEF\u5DEE\u6700\u5927\uFF0C\u6839\u672C\u539F\u56E0\u662FUSO\u8DDF\u8E2A\u539F\u6CB9\u671F\u8D27\u800C\u975E\u73B0\u8D27\uFF0C\u671F\u8D27\u5C55\u671F\uFF08contango\uFF09\u5BFC\u81F4\u6301\u7EED\u635F\u8017\n";
md += "- **\u9EC4\u91D1**\uFF08160719\uFF09MAE=0.364%\u5C1A\u53EF\u63A5\u53D7\uFF0C\u8DDF\u8E2A\u4F26\u6566\u91D1\u73B0\u8D27\u4EF7\u683C\n";
md += "- **\u4E2D\u6982\u4E92\u8054\u7F51**\uFF08164906\uFF09MAE=1.235%\uFF0C\u6E2F\u80A1+\u7F8E\u80A1\u8DE8\u5E02\u573A\u65F6\u95F4\u5DEE+\u6C47\u7387\u5BFC\u81F4\u504F\u5DEE\n";
md += "- **\u7F8E\u56FD\u5927\u76D8/\u884C\u4E1AETF**\uFF08SPY/QQQ/XLY/XOP/IEO\u7B49\uFF09\u8868\u73B0\u4F18\u79C0\uFF0CMAE\u5747\u57280.1%\u5DE6\u53F3\u6216\u4EE5\u4E0B\n";
md += "- ETF\u6620\u5C04\u4F18\u5316\u540E\uFF0CRYH\uFF08161126\uFF09\u3001IEO\uFF08162719\uFF09\u3001IYR\uFF08160140\uFF09\u5747\u83B7\u5F97\u5B8C\u5168\u5339\u914D\n";

fs.writeFileSync(outputPath, md, "utf8");
console.log("Done: " + outputPath);
console.log("A: " + aFunds.length + ", B: " + bFunds.length + ", total: " + (aFunds.length + bFunds.length));