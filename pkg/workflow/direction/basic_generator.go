package direction

type BasicDirectionGenerator struct{}

func NewBasicDirectionGenerator() *BasicDirectionGenerator {
	return &BasicDirectionGenerator{}
}

func (b *BasicDirectionGenerator) Generate(state interface{}, priorities interface{}) (interface{}, error) {
	// TODO: Implement actual direction generation logic
	return "Default direction", nil
}

func (b *BasicDirectionGenerator) GenerateForInsufficiency(state interface{}, priorities interface{}, reason string) (interface{}, error) {
	// TODO: Implement direction generation logic for insufficiency
	return "Default direction for insufficiency", nil
}
