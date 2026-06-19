from string import Template

#### HyDE PROMPT ####

system_prompt = Template("\n".join([
    "You are an expert academic researcher at the College of Engineering, Minia University.",
    "Please write a scientific and informative paragraph in Arabic that answers the user's question.",
    "The paragraph should look like an excerpt from an official university handbook, department guide, or student bylaws.",
    "Do not include introductory phrases like 'Here is the answer' or 'According to the documents'.",
    "Focus on technical accuracy and university-specific terminology.",
    "The length should be approximately 400-500 characters.",
]))

document_prompt = Template("""
## Example 1
**Question:** ما هي شروط القبول في قسم هندسة الحاسبات؟
**Hypothetical Document:** يتطلب الالتحاق بقسم هندسة الحاسبات والنظم بكلية الهندسة جامعة المنيا اجتياز الطالب للفرقة الإعدادية بتقدير عام مناسب وفقاً للتنسيق الداخلي للكلية في تلك السنة. تعتمد المفاضلة بين الطلاب على مجموع درجات الطالب في المواد الأساسية وخاصة الرياضيات والفيزياء، بالإضافة إلى الطاقة الاستيعابية للقسم التي يحددها مجلس الكلية. يجب على الطلاب الراغبين في التحويل استيفاء الشروط واللوائح الداخلية التي تنظم عملية التوزيع على الأقسام العلمية المختلفة لضمان جودة العملية التعليمية.

## Example 2
**Question:** كيف يمكنني استخراج بيان نجاح من الكلية؟
**Hypothetical Document:** لاستخراج بيان نجاح رسمي من كلية الهندسة بجامعة المنيا، يجب على الطالب التوجه إلى شؤون الطلاب لسحب نموذج طلب استخراج الشهادة. يتطلب الأمر تقديم صورة من بطاقة الرقم القومي، وسداد الرسوم المقررة عبر منظومة الدفع الإلكتروني (فوري) أو الخزينة المركزية. بعد التأكد من عدم وجود أي إخلاء طرف معلق، يتم مراجعة الملف الأكاديمي للطالب واعتماد البيان من وكيل الكلية لشؤون التعليم والطلاب وعميد الكلية، وعادة ما تستغرق الدورة المستندية من يومين إلى ثلاثة أيام عمل.

## Example 3
**Question:** ما هو نظام الساعات المعتمدة في لائحة الكلية الجديدة؟
**Hypothetical Document:** تعتمد لائحة كلية الهندسة جامعة المنيا الحديثة نظام الساعات المعتمدة كإطار دراسي يمنح الطالب مرونة في اختيار المقررات وتسجيلها. يتطلب نيل درجة البكالوريوس إتمام عدد محدد من الساعات المعتمدة بنجاح، مقسمة بين متطلبات الجامعة، والكلية، والتخصص الإجباري والاختياري. يتم تقييم أداء الطالب بناءً على المعدل التراكمي (GPA)، حيث يشرف المرشد الأكاديمي على اختيار الطالب للمقررات في بداية كل فصل دراسي لضمان توافق الجدول الزمني مع قدرات الطالب والمتطلبات الأكاديمية للقسم.
""")

footer_prompt = Template("\n".join([
    "## Question:",
    "$query",
    "",
    "## Hypothetical Document:",
]))