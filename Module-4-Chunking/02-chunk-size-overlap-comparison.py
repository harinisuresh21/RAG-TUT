from langchain.text_splitter import RecursiveCharacterTextSplitter

hr_policy_text = """Employee Leave Policy

Annual Leave
Every full-time employee receives 30 paid annual leave days per year. Leave requests must be submitted through the HR portal at least two weeks in advance. Approval is granted by the employee's direct manager.

Sick Leave
Full-time employees receive 15 paid sick leave days per year. A medical certificate is required if sick leave extends beyond three consecutive days. Unused sick leave does not carry over to the following year.

Carry-Over Policy
Up to 10 unused annual leave days may be carried forward into the next calendar year. Carried-over days must be used before the end of the first quarter of the new year or they are forfeited.

Parental Leave
Employees are entitled to 12 weeks of paid parental leave. This applies to birth, adoption, and surrogacy. Employees must notify HR at least 30 days before the expected start date.

Special Leave
Bereavement leave is granted for up to 5 working days. Jury duty leave is paid for up to 10 working days. Both require supporting documentation to be submitted to HR within 14 days.
"""


def split_and_report(text, chunk_size, chunk_overlap):
    """Split the same text with one (chunk_size, chunk_overlap) setting and report the results"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = splitter.split_text(text)

    print(f"Settings: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    print(f"Result: {len(chunks)} chunk(s)")

    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n  Chunk {i} ({len(chunk)} characters):")
        print(f'  "{chunk[:120]}...')

    if len(chunks) > 3:
        print(f"\n  ... and {len(chunks) - 3} more chunk(s)")

    print()
    return chunks


def main():
    """Compare RecursiveCharacterTextSplitter at three different size/overlap settings"""
    print("=== Chunk Size & Overlap Comparison ===\n")
    print(f"Input text: {len(hr_policy_text)} characters of company policy text.\n")

    print("=" * 60)
    print("1. TINY CHUNKS   ->  chunk_size=50,   chunk_overlap=0")
    print("   Many precise but tiny chunks; context is easily lost.")
    print("=" * 60)
    split_and_report(hr_policy_text, chunk_size=50, chunk_overlap=0)

    print("=" * 60)
    print("2. MEDIUM CHUNKS ->  chunk_size=200,  chunk_overlap=20")
    print("   A middle ground: more context, still fairly focused.")
    print("=" * 60)
    split_and_report(hr_policy_text, chunk_size=200, chunk_overlap=20)

    print("=" * 60)
    print("3. LARGE CHUNKS  ->  chunk_size=500,  chunk_overlap=100")
    print("   Context-rich but fewer, noisier chunks.")
    print("=" * 60)
    split_and_report(hr_policy_text, chunk_size=500, chunk_overlap=100)

    print("\n=== Done. Compare the chunk counts and previews above. ===")


if __name__ == "__main__":
    main()
