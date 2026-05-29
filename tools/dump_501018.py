import pdfplumber
pdf = pdfplumber.open('runtime_data/qreport/AN202604211821393105.pdf')
full = chr(10).join([p.extract_text() or '' for p in pdf.pages])
# Print from char 4500 to end
print(full[4500:])