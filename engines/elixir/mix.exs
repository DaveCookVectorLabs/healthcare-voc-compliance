defmodule HealthcareVoc.MixProject do
  use Mix.Project

  def project do
    [
      app: :healthcare_voc,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      description: description(),
      package: package(),
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger]
    ]
  end

  defp deps do
    [
      {:ex_doc, "~> 0.31", only: :dev, runtime: false}
    ]
  end

  defp description do
    "Healthcare VOC compliance calculator — computes VOC exposure, OSHA PEL comparison, and multi-jurisdiction regulatory compliance for cleaning products."
  end

  defp package do
    [
      name: "healthcare_voc",
      licenses: ["MIT"],
      links: %{
        "GitHub" => "https://github.com/DaveCookVectorLabs/healthcare-voc-compliance",
        "Binx Professional Cleaning" => "https://www.binx.ca/commercial.php"
      },
      maintainers: ["Dave Cook"]
    ]
  end
end
