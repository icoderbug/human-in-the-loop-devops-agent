from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(
    project,
    review,
    risk,
    docker,
    k8s,
    cicd
):

    pdf_file = "DevOps_Report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Human-in-the-Loop DevOps Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    sections = [
        ("Project", project),
        ("Review", review),
        ("Risk", risk),
        ("Dockerfile", docker),
        ("Kubernetes", k8s),
        ("CI/CD", cicd)
    ]

    for title, text in sections:

        content.append(
            Paragraph(
                f"<b>{title}</b>",
                styles["Heading2"]
            )
        )

        content.append(
            Paragraph(
                str(text),
                styles["BodyText"]
            )
        )

        content.append(
            Spacer(1, 10)
        )

    doc.build(content)

    return pdf_file