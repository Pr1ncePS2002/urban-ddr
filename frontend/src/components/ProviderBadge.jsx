const ProviderBadge = ({ provider, type }) => {
    return (
        <span style={{
            fontSize: '0.7rem',
            padding: '2px 6px',
            borderRadius: '4px',
            background: 'rgba(255,255,255,0.1)',
            border: '1px solid rgba(255,255,255,0.2)',
            marginRight: '4px'
        }}>
            {type}: {provider}
        </span>
    );
};
export default ProviderBadge;
