# Homebrew Formula for GenomeMCP
# 
# This file should be placed in a separate Homebrew tap repository:
#   github.com/nexisdev/homebrew-genomemcp
#
# Installation:
#   brew tap nexisdev/genomemcp
#   brew install genomemcp

class Genomemcp < Formula
  include Language::Python::Virtualenv

  desc "CLI for genomic intelligence - ClinVar, gnomAD, Reactome, PubMed"
  homepage "https://github.com/nexisdev/GenomeMCP"
  url "https://files.pythonhosted.org/packages/source/g/genomemcp/genomemcp-0.1.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"
  head "https://github.com/nexisdev/GenomeMCP.git", branch: "main"

  depends_on "python@3.11"

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/source/h/httpx/httpx-0.27.0.tar.gz"
    sha256 "REPLACE_WITH_ACTUAL_SHA256"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.21.1.tar.gz"
    sha256 "REPLACE_WITH_ACTUAL_SHA256"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-14.2.0.tar.gz"
    sha256 "REPLACE_WITH_ACTUAL_SHA256"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "GenomeMCP", shell_output("#{bin}/genomemcp --help")
  end
end
