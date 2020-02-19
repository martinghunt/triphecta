import logging

from triphecta import vcf


class StrainTriple:
    def __init__(self, case, control1, control2):
        self.case = case
        self.control1 = control1
        self.control2 = control2
        self.variant_calls = {"case": None, "control1": None, "control2": None}
        self.variants = None
        self.variant_indexes_of_interest = set()

    def __eq__(self, other):
        return type(other) is type(self) and self.__dict__ == other.__dict__

    def set_variants(self, variants):
        self.variants = variants

    def load_variants_from_vcf_files(self, case_vcf, control1_vcf, control2_vcf):
        logging.info(f"Loading VCF file {case_vcf}")
        self.variant_calls[
            "case"
        ], self.variants = vcf.load_variant_calls_from_vcf_file(
            case_vcf, expected_variants=self.variants
        )
        logging.info(f"Loading VCF file {control1_vcf}")
        self.variant_calls["control1"], _ = vcf.load_variant_calls_from_vcf_file(
            control1_vcf, expected_variants=self.variants
        )
        logging.info(f"Loading VCF file {control2_vcf}")
        self.variant_calls["control2"], _ = vcf.load_variant_calls_from_vcf_file(
            control2_vcf, expected_variants=self.variants
        )

    def update_variants_of_interest(self):
        self.variant_indexes_of_interest = set()

        for i, variant in enumerate(self.variants):
            # We are interested in where the two controls have the same
            # genotype call, and the case genotype call is different.
            # We can't say anything about null calls, so skip those.
            if (
                self.variant_calls["case"][i] == "."
                or self.variant_calls["control1"][i] == "."
                or self.variant_calls["control2"][i] == "."
                or self.variant_calls["control1"][i]
                != self.variant_calls["control2"][i]
                or self.variant_calls["case"] == self.variant_calls["control1"]
            ):
                continue

            self.variant_indexes_of_interest.add(i)
