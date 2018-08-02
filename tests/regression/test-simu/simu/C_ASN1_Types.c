#include <stdio.h>
#include <string.h>

#include <assert.h>

#include "C_ASN1_Types.h"

#ifdef __NEED_MyChoice_UPER
size_t Encode_UPER_MyChoice(void *pBuffer, size_t iMaxBufferSize, const asn1SccMyChoice *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMyChoice_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MyChoice (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MyChoice_ACN
size_t Encode_ACN_MyChoice(void *pBuffer, size_t iMaxBufferSize, asn1SccMyChoice *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMyChoice_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MyChoice (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MyChoice_NATIVE
size_t Encode_NATIVE_MyChoice(void *pBuffer, size_t iMaxBufferSize, const asn1SccMyChoice *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccMyChoice) );
    return sizeof(asn1SccMyChoice);
}
#endif

#ifdef __NEED_MyChoice_UPER
int Decode_UPER_MyChoice(asn1SccMyChoice *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMyChoice_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MyChoice (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MyChoice_ACN
int Decode_ACN_MyChoice(asn1SccMyChoice *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMyChoice_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MyChoice (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MyChoice_NATIVE
int Decode_NATIVE_MyChoice(asn1SccMyChoice *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccMyChoice *) pBuffer;
    {
        return 0;
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_list_UPER
size_t Encode_UPER_TASTE_Peek_id_list(void *pBuffer, size_t iMaxBufferSize, const asn1SccTASTE_Peek_id_list *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccTASTE_Peek_id_list_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode TASTE-Peek-id-list (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_list_ACN
size_t Encode_ACN_TASTE_Peek_id_list(void *pBuffer, size_t iMaxBufferSize, asn1SccTASTE_Peek_id_list *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccTASTE_Peek_id_list_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode TASTE-Peek-id-list (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_list_NATIVE
size_t Encode_NATIVE_TASTE_Peek_id_list(void *pBuffer, size_t iMaxBufferSize, const asn1SccTASTE_Peek_id_list *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccTASTE_Peek_id_list) );
    return sizeof(asn1SccTASTE_Peek_id_list);
}
#endif

#ifdef __NEED_TASTE_Peek_id_list_UPER
int Decode_UPER_TASTE_Peek_id_list(asn1SccTASTE_Peek_id_list *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccTASTE_Peek_id_list_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode TASTE-Peek-id-list (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_list_ACN
int Decode_ACN_TASTE_Peek_id_list(asn1SccTASTE_Peek_id_list *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccTASTE_Peek_id_list_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode TASTE-Peek-id-list (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_list_NATIVE
int Decode_NATIVE_TASTE_Peek_id_list(asn1SccTASTE_Peek_id_list *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccTASTE_Peek_id_list *) pBuffer;
    {
        return 0;
    }
}
#endif

#ifdef __NEED_MySetOf_UPER
size_t Encode_UPER_MySetOf(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySetOf *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMySetOf_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MySetOf (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MySetOf_ACN
size_t Encode_ACN_MySetOf(void *pBuffer, size_t iMaxBufferSize, asn1SccMySetOf *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMySetOf_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MySetOf (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MySetOf_NATIVE
size_t Encode_NATIVE_MySetOf(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySetOf *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccMySetOf) );
    return sizeof(asn1SccMySetOf);
}
#endif

#ifdef __NEED_MySetOf_UPER
int Decode_UPER_MySetOf(asn1SccMySetOf *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMySetOf_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MySetOf (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MySetOf_ACN
int Decode_ACN_MySetOf(asn1SccMySetOf *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMySetOf_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MySetOf (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MySetOf_NATIVE
int Decode_NATIVE_MySetOf(asn1SccMySetOf *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccMySetOf *) pBuffer;
    {
        return 0;
    }
}
#endif

#ifdef __NEED_MyEnum_UPER
size_t Encode_UPER_MyEnum(void *pBuffer, size_t iMaxBufferSize, const asn1SccMyEnum *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMyEnum_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MyEnum (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MyEnum_ACN
size_t Encode_ACN_MyEnum(void *pBuffer, size_t iMaxBufferSize, asn1SccMyEnum *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMyEnum_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MyEnum (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MyEnum_NATIVE
size_t Encode_NATIVE_MyEnum(void *pBuffer, size_t iMaxBufferSize, const asn1SccMyEnum *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccMyEnum) );
    return sizeof(asn1SccMyEnum);
}
#endif

#ifdef __NEED_MyEnum_UPER
int Decode_UPER_MyEnum(asn1SccMyEnum *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMyEnum_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MyEnum (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MyEnum_ACN
int Decode_ACN_MyEnum(asn1SccMyEnum *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMyEnum_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MyEnum (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MyEnum_NATIVE
int Decode_NATIVE_MyEnum(asn1SccMyEnum *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccMyEnum *) pBuffer;
    {
        return 0;
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_UPER
size_t Encode_UPER_TASTE_Peek_id(void *pBuffer, size_t iMaxBufferSize, const asn1SccTASTE_Peek_id *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccTASTE_Peek_id_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode TASTE-Peek-id (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_ACN
size_t Encode_ACN_TASTE_Peek_id(void *pBuffer, size_t iMaxBufferSize, asn1SccTASTE_Peek_id *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccTASTE_Peek_id_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode TASTE-Peek-id (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_NATIVE
size_t Encode_NATIVE_TASTE_Peek_id(void *pBuffer, size_t iMaxBufferSize, const asn1SccTASTE_Peek_id *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccTASTE_Peek_id) );
    return sizeof(asn1SccTASTE_Peek_id);
}
#endif

#ifdef __NEED_TASTE_Peek_id_UPER
int Decode_UPER_TASTE_Peek_id(asn1SccTASTE_Peek_id *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccTASTE_Peek_id_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode TASTE-Peek-id (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_ACN
int Decode_ACN_TASTE_Peek_id(asn1SccTASTE_Peek_id *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccTASTE_Peek_id_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode TASTE-Peek-id (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_TASTE_Peek_id_NATIVE
int Decode_NATIVE_TASTE_Peek_id(asn1SccTASTE_Peek_id *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccTASTE_Peek_id *) pBuffer;
    {
        return 0;
    }
}
#endif

#ifdef __NEED_MySeq_UPER
size_t Encode_UPER_MySeq(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySeq *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMySeq_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MySeq (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MySeq_ACN
size_t Encode_ACN_MySeq(void *pBuffer, size_t iMaxBufferSize, asn1SccMySeq *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMySeq_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MySeq (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MySeq_NATIVE
size_t Encode_NATIVE_MySeq(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySeq *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccMySeq) );
    return sizeof(asn1SccMySeq);
}
#endif

#ifdef __NEED_MySeq_UPER
int Decode_UPER_MySeq(asn1SccMySeq *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMySeq_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MySeq (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MySeq_ACN
int Decode_ACN_MySeq(asn1SccMySeq *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMySeq_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MySeq (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MySeq_NATIVE
int Decode_NATIVE_MySeq(asn1SccMySeq *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccMySeq *) pBuffer;
    {
        return 0;
    }
}
#endif

#ifdef __NEED_T_UInt32_UPER
size_t Encode_UPER_T_UInt32(void *pBuffer, size_t iMaxBufferSize, const asn1SccT_UInt32 *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccT_UInt32_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode T-UInt32 (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_T_UInt32_ACN
size_t Encode_ACN_T_UInt32(void *pBuffer, size_t iMaxBufferSize, asn1SccT_UInt32 *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccT_UInt32_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode T-UInt32 (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_T_UInt32_NATIVE
size_t Encode_NATIVE_T_UInt32(void *pBuffer, size_t iMaxBufferSize, const asn1SccT_UInt32 *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccT_UInt32) );
    return sizeof(asn1SccT_UInt32);
}
#endif

#ifdef __NEED_T_UInt32_UPER
int Decode_UPER_T_UInt32(asn1SccT_UInt32 *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccT_UInt32_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode T-UInt32 (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_T_UInt32_ACN
int Decode_ACN_T_UInt32(asn1SccT_UInt32 *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccT_UInt32_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode T-UInt32 (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_T_UInt32_NATIVE
int Decode_NATIVE_T_UInt32(asn1SccT_UInt32 *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccT_UInt32 *) pBuffer;
    {
        return 0;
    }
}
#endif

#ifdef __NEED_MySimpleSeq_UPER
size_t Encode_UPER_MySimpleSeq(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySimpleSeq *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMySimpleSeq_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MySimpleSeq (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MySimpleSeq_ACN
size_t Encode_ACN_MySimpleSeq(void *pBuffer, size_t iMaxBufferSize, asn1SccMySimpleSeq *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMySimpleSeq_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MySimpleSeq (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MySimpleSeq_NATIVE
size_t Encode_NATIVE_MySimpleSeq(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySimpleSeq *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccMySimpleSeq) );
    return sizeof(asn1SccMySimpleSeq);
}
#endif

#ifdef __NEED_MySimpleSeq_UPER
int Decode_UPER_MySimpleSeq(asn1SccMySimpleSeq *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMySimpleSeq_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MySimpleSeq (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MySimpleSeq_ACN
int Decode_ACN_MySimpleSeq(asn1SccMySimpleSeq *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMySimpleSeq_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MySimpleSeq (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MySimpleSeq_NATIVE
int Decode_NATIVE_MySimpleSeq(asn1SccMySimpleSeq *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccMySimpleSeq *) pBuffer;
    {
        return 0;
    }
}
#endif

#ifdef __NEED_FixedIntList_UPER
size_t Encode_UPER_FixedIntList(void *pBuffer, size_t iMaxBufferSize, const asn1SccFixedIntList *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccFixedIntList_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode FixedIntList (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_FixedIntList_ACN
size_t Encode_ACN_FixedIntList(void *pBuffer, size_t iMaxBufferSize, asn1SccFixedIntList *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccFixedIntList_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode FixedIntList (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_FixedIntList_NATIVE
size_t Encode_NATIVE_FixedIntList(void *pBuffer, size_t iMaxBufferSize, const asn1SccFixedIntList *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccFixedIntList) );
    return sizeof(asn1SccFixedIntList);
}
#endif

#ifdef __NEED_FixedIntList_UPER
int Decode_UPER_FixedIntList(asn1SccFixedIntList *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccFixedIntList_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode FixedIntList (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_FixedIntList_ACN
int Decode_ACN_FixedIntList(asn1SccFixedIntList *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccFixedIntList_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode FixedIntList (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_FixedIntList_NATIVE
int Decode_NATIVE_FixedIntList(asn1SccFixedIntList *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccFixedIntList *) pBuffer;
    {
        return 0;
    }
}
#endif

#ifdef __NEED_MySeqOf_UPER
size_t Encode_UPER_MySeqOf(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySeqOf *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMySeqOf_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MySeqOf (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MySeqOf_ACN
size_t Encode_ACN_MySeqOf(void *pBuffer, size_t iMaxBufferSize, asn1SccMySeqOf *pSrc)
{
    (void)iMaxBufferSize;
    int errorCode;
    STATIC BitStream strm;

    BitStream_Init(&strm, pBuffer, iMaxBufferSize);
    if (asn1SccMySeqOf_ACN_Encode(pSrc, &strm, &errorCode, TRUE) == FALSE) {
	fprintf(stderr, "Could not encode MySeqOf (at %s, %d), errorCode was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    } else {
        return BitStream_GetLength(&strm);
    }
}
#endif

#ifdef __NEED_MySeqOf_NATIVE
size_t Encode_NATIVE_MySeqOf(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySeqOf *pSrc)
{
    (void)iMaxBufferSize;
    memcpy(pBuffer, pSrc, sizeof(asn1SccMySeqOf) );
    return sizeof(asn1SccMySeqOf);
}
#endif

#ifdef __NEED_MySeqOf_UPER
int Decode_UPER_MySeqOf(asn1SccMySeqOf *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMySeqOf_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MySeqOf (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MySeqOf_ACN
int Decode_ACN_MySeqOf(asn1SccMySeqOf *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    int errorCode;

    STATIC BitStream strm;

    BitStream_AttachBuffer(&strm, pBuffer, iBufferSize);

    if (asn1SccMySeqOf_ACN_Decode(pDst, &strm, &errorCode)) {
        /* Decoding succeeded */
        return 0;
    } else {
	fprintf(stderr, "Could not decode MySeqOf (at %s, %d), error code was %d\n", __FILE__, __LINE__, errorCode);
        return -1;
    }
}
#endif

#ifdef __NEED_MySeqOf_NATIVE
int Decode_NATIVE_MySeqOf(asn1SccMySeqOf *pDst, void *pBuffer, size_t iBufferSize)
{
    (void)iBufferSize;
    *pDst = *(asn1SccMySeqOf *) pBuffer;
    {
        return 0;
    }
}
#endif

