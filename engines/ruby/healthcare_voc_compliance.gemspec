Gem::Specification.new do |s|
  s.name        = 'healthcare_voc_compliance'
  s.version     = '0.1.0'
  s.summary     = 'Healthcare VOC compliance calculator'
  s.description = 'Computes VOC exposure, OSHA PEL comparison, and multi-jurisdiction regulatory compliance for cleaning products used in healthcare facilities.'
  s.authors     = ['Dave Cook']
  s.email       = 'dave@binx.ca'
  s.homepage    = 'https://github.com/DaveCookVectorLabs/healthcare-voc-compliance'
  s.license     = 'MIT'
  s.files       = ['lib/healthcare_voc_compliance.rb']
  s.metadata    = {
    'source_code_uri' => 'https://github.com/DaveCookVectorLabs/healthcare-voc-compliance',
    'homepage_uri'    => 'https://www.binx.ca/commercial.php',
  }
  s.required_ruby_version = '>= 3.0'
end
