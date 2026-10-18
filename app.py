from io import BytesIO
import pypdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st

st.set_page_config(
    page_title="LIC Form PDF Stamping Portal", page_icon="🖨️", layout="wide"
)

st.title("🩺 LIC & Health India TPA - Official PDF Form Stamping App")
st.markdown(
    "Upload your blank LIC PDF form below, fill in the patient details, and this"
    " app will stamp your text directly onto the document."
)

# File uploader for the blank template PDF
uploaded_file = st.file_uploader(
    "Upload Blank LIC PDF Form (e.g., NEW FORMS LIC (2).pdf)", type=["pdf"]
)

if uploaded_file is not None:
  st.success("Blank PDF uploaded successfully! Fill in the details below.")

  with st.form("overlay_form"):
    st.subheader("1. Patient & Policy Details")
    col1, col2 = st.columns(2)
    with col1:
      proposal_no = st.text_input("Proposal / Policy Number")
      la_name = st.text_input("Full Name of Life Assured")
      age_gender = st.text_input("Age / Gender", value="35 / Male")
    with col2:
      mobile = st.text_input("Mobile Number")
      id_proof = st.text_input("ID Proof & No (Last 4 digits)")

    st.subheader("2. Physical Vitals")
    col3, col4, col5, col6 = st.columns(4)
    with col3:
      height = st.text_input("Height (cm)", value="170")
    with col4:
      weight = st.text_input("Weight (kg)", value="70")
    with col5:
      pulse = st.text_input("Pulse (bpm)", value="72")
    with col6:
      bp = st.text_input("Blood Pressure", value="120/80")

    st.subheader(
        "3. Text Position Adjustment (Coordinates from bottom-left corner)"
    )
    st.markdown(
        "You can adjust where the text starts printing on Page 1 if needed."
    )
    c_x, c_y = st.columns(2)
    with c_x:
      x_pos = st.number_input(
          "X Position (Left margin in points)", value=120.0
      )
    with c_y:
      y_pos = st.number_input(
          "Y Position (Bottom margin in points)", value=640.0
      )

    submitted = st.form_submit_button("Generate Stamped PDF")

  if submitted:
    if not proposal_no or not la_name:
      st.error("Please fill in at least the Proposal Number and Name.")
    else:
      # Create transparent overlay sheet using ReportLab
      packet = BytesIO()
      can = canvas.Canvas(packet, pagesize=letter)
      can.setFont("Helvetica", 10)

      # Draw text fields line by line downwards from the Y position
      current_y = y_pos
      line_spacing = 16

      can.drawString(x_pos, current_y, f"{proposal_no}")
      current_y -= line_spacing * 2.5
      can.drawString(x_pos, current_y, f"{la_name}")
      current_y -= line_spacing * 1.5
      can.drawString(x_pos, current_y, f"{age_gender}")
      current_y -= line_spacing * 1.5
      can.drawString(
          x_pos, current_y, f"Mobile: {mobile} | ID: {id_proof}"
      )
      current_y -= line_spacing * 1.5
      can.drawString(
          x_pos,
          current_y,
          f"Ht: {height}cm | Wt: {weight}kg | Pulse: {pulse} | BP: {bp}",
      )

      can.save()
      packet.seek(0)

      # Load original PDF and overlay packet
      original_pdf = pypdf.PdfReader(uploaded_file)
      overlay_pdf = pypdf.PdfReader(packet)

      output_pdf = pypdf.PdfWriter()

      # Merge overlay onto the first page of the original PDF
      page = original_pdf.pages[0]
      page.merge_page(overlay_pdf.pages[0])
      output_pdf.add_page(page)

      # Append any remaining pages unmodified
      for i in range(1, len(original_pdf.pages)):
        output_pdf.add_page(original_pdf.pages[i])

      output_buffer = BytesIO()
      output_pdf.write(output_buffer)
      output_buffer.seek(0)

      st.success(
          "Official PDF successfully stamped! Download your completed form"
          " below."
      )
      st.download_button(
          label="📥 Download Stamped LIC PDF",
          data=output_buffer,
          file_name=f"Stamped_LIC_{proposal_no}.pdf",
          mime="application/pdf",
      )
else:
  st.info(
      "👆 Please upload your blank LIC PDF form using the file uploader above"
      " to get started."
  )
