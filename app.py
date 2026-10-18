from datetime import datetime
from io import BytesIO
import pypdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st

st.set_page_config(
    page_title="LIC Official PDF Stamping Portal", page_icon="🖨️", layout="wide"
)

st.title("🩺 LIC & Health India TPA - Official Form Stamping Tool")
st.markdown(
    "This tool takes your **official blank LIC PDF form**, places your typed"
    " patient data directly onto the blank spaces, and outputs the completed"
    " official document."
)

# 1. File Uploader for the official blank form
uploaded_file = st.file_uploader(
    "Upload Official Blank LIC PDF Form (e.g., Lic forms-1.pdf)", type=["pdf"]
)

if uploaded_file is not None:
  st.success(
      "Official form template loaded! Fill in the details below to stamp them"
      " onto the document."
  )

  with st.form("stamping_form"):
    st.subheader("1. Patient & Policy Details")
    col1, col2, col3 = st.columns(3)
    with col1:
      proposal_no = st.text_input("Proposal No", value="")
    with col2:
      la_name = st.text_input("Name of Life Assured / Proposer", value="")
    with col3:
      exam_date = st.text_input(
          "Date", value=datetime.today().strftime("%d/%m/%Y")
      )

    st.subheader("2. Identity Proof Verification")
    col4, col5 = st.columns(2)
    with col4:
      id_type = st.selectbox(
          "Select Verified Photo ID Type",
          [
              "Aadhaar Card",
              "PAN Card",
              "Driving License",
              "Ration Card",
              "Passport",
              "Employment Identity Card",
          ],
      )
    with col5:
      id_details = st.text_input(
          "ID Number / Details (e.g. Last 4 digits)", value=""
      )

    st.subheader("3. Clinical Vitals & Mobile")
    col6, col7, col8 = st.columns(3)
    with col6:
      mobile_no = st.text_input("Mobile Number", value="")
    with col7:
      height_weight = st.text_input("Height & Weight", value="170 cm / 70 kg")
    with col8:
      bp_pulse = st.text_input("BP & Pulse", value="120/80 mmHg | 72 bpm")

    st.markdown("---")
    with st.expander(
        "⚙️ Fine-Tune Print Coordinates (Adjust if text alignment needs"
        " shifting)"
    ):
      st.markdown(
          "Use these controls to move where the text prints on the page."
      )
      c_x, c_y = st.columns(2)
      with c_x:
        start_x = st.number_input(
            "Horizontal Position (X Offset)",
            value=160.0,
            help="Higher moves text right",
        )
      with c_y:
        start_y = st.number_input(
            "Vertical Position (Y Offset from top)",
            value=740.0,
            help="Lower moves text down",
        )

    submitted = st.form_submit_button("Stamp & Generate Official PDF")

  if submitted:
    if not proposal_no or not la_name:
      st.error(
          "Please enter at least the Proposal Number and Life Assured Name."
      )
    else:
      # Create transparent overlay sheet using ReportLab
      packet = BytesIO()
      # Standard Letter page size in points: 612 x 792
      can = canvas.Canvas(packet, pagesize=letter)
      can.setFont("Helvetica-Bold", 10)

      # Stamping data onto precise coordinate slots
      y = start_y

      # Proposal No & Date row
      can.drawString(start_x, y, f"{proposal_no}")
      can.drawString(start_x + 240, y, f"{exam_date}")

      # Name row
      y -= 22
      can.drawString(start_x, y, f"{la_name}")

      # Identity proof section mapping based on selected type
      id_offsets = {
          "Aadhaar Card": 105,
          "PAN Card": 122,
          "Driving License": 138,
          "Ration Card": 155,
          "Passport": 172,
          "Employment Identity Card": 190,
      }
      target_id_drop_y = start_y - id_offsets.get(id_type, 122)
      can.drawString(start_x + 100, target_id_drop_y, f": {id_details}")

      # Mobile and Vitals lower down the page
      can.drawString(
          start_x,
          start_y - 250,
          f"Mobile: {mobile_no} | {height_weight} | {bp_pulse}",
      )

      can.save()
      packet.seek(0)

      # Load original template PDF and overlay packet
      original_pdf = pypdf.PdfReader(uploaded_file)
      overlay_pdf = pypdf.PdfReader(packet)

      output_pdf = pypdf.PdfWriter()

      # Merge the overlay transparent sheet onto Page 1 of the official form
      page = original_pdf.pages[0]
      page.merge_page(overlay_pdf.pages[0])
      output_pdf.add_page(page)

      # Copy any remaining pages (like page 2) untouched from the original form
      for i in range(1, len(original_pdf.pages)):
        output_pdf.add_page(original_pdf.pages[i])

      output_buffer = BytesIO()
      output_pdf.write(output_buffer)
      output_buffer.seek(0)

      st.success(
          "Official form stamped successfully! The background template remains"
          " completely intact."
      )
      st.download_button(
          label="📥 Download Stamped Official PDF",
          data=output_buffer,
          file_name=f"Official_Stamped_LIC_{proposal_no}.pdf",
          mime="application/pdf",
      )
else:
  st.info(
      "👆 Please upload your blank official LIC form PDF using the file"
      " uploader above to begin."
  )
