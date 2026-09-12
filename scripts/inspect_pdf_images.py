import fitz
import sys

def inspect_pdf(pdf_path):
    print(f"Inspecting {pdf_path}...")
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            print(f"Page {page_num}: found {len(image_list)} images")
            for i, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                print(f"  Image {i}: xref={xref}, width={pix.w}, height={pix.h}, channels={pix.n}, area={pix.w * pix.h}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inspect_pdf(sys.argv[1])
